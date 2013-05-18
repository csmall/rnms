# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011,2012 Craig Small <csmall@enc.com.au>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>
#
#
""" JFFNMS data importer """
import datetime
import transaction

from sqlalchemy.exc import IntegrityError

from rnms import model
from rnms.lib import states
from rnms.model import DBSession

#        for oldid in (1,4,5,6,7,8,9,10,11,12):
#            self.slas[oldid] = newid
#            newid += 1



def get_interface_index(obj,int_id):
    result = obj.dbhandle.execute('SELECT interfaces_values.value from interfaces_values,interface_types_fields where interface=%d and interfaces_values.field=interface_types_fields.id AND interface_types_fields.ftype=3'%int_id)
    for row in result:
        return row[0]
    return ''

def do_delete(obj):
    del_items = (
        ('EventField', None),
        ('Event', None),
        ('AttributeField', None),
        ('Attribute', 1),
        ('Iface', None),
        ('Host', 1),
        ('Zone', 1),
    )
    for model_name, del_id in del_items:
        m = getattr(model, model_name)
        del_count = delete_all(m, del_id)
        obj.logger.info('%d rows deleted from %s',del_count, model_name)
    obj.logger.info('%d rows deleted from User', delete_users())
    transaction.commit()

def delete_all(del_model, del_id=None):
    """ Delete all items of del_model with an ID higher than del_id 
        Returns number of deleted items
    """
    deleted_items=0
    if del_id is None:
        deleted_items = DBSession.query(del_model).delete()
    else:
        deleted_items = DBSession.query(del_model).filter(del_model.id>del_id).delete()
    if deleted_items is None:
        return 0
    return deleted_items

def delete_users():
    """ Delete all items of del_model with an ID higher than del_id 
        Returns number of deleted items
    """
    deleted_items = DBSession.query(model.User).filter(model.User.user_id>2).delete()
    if deleted_items is None:
        return 0
    return deleted_items

def import_attribute(obj):
    attribute_count=0
    attributes = {}
    field_count=0
    up_state = model.EventState.get_up()
    try:
        result = obj.dbhandle.execute('SELECT interfaces.*,interface_types.description as itype, pollers_groups.description, slas.description FROM interfaces LEFT JOIN slas ON (slas.id=interfaces.sla),interface_types,pollers_groups WHERE host > 1 AND interfaces.type=interface_types.id AND interfaces.poll=pollers_groups.id ORDER BY interfaces.id')
        for row in result:
            att = model.Attribute()
            att.display_name=row[2]
            att.host_id = obj.host_id(row[3])
            att.index = get_interface_index(obj, row[0])
            att.user_id = obj.user_id(row[4])
            #FIXME poll group
            att.make_sound = bool(row[7])
            # show_rootmap is visible and admin_state
            if row[8] == 0:
                att.visible = False
            elif row[8] == 1:
                att.admin_state = states.STATE_UP
            elif row[8] == 2:
                att.admin_state = states.STATE_DOWN
            att.created = datetime.datetime.fromtimestamp(row[10])
            att.updated = datetime.datetime.fromtimestamp(row[11])
            att.next_poll = datetime.datetime.fromtimestamp(row[12]) + datetime.timedelta(minutes=5)
            att.attribute_type = DBSession.query(model.AttributeType).filter(model.AttributeType.display_name==unicode(row[15])).first()

            if row[16] == 'SNMP Interface HC':
                att.poller_set = DBSession.query(model.PollerSet).filter(model.PollerSet.display_name==unicode('SNMP Interface')).first()
            else:
                att.poller_set = DBSession.query(model.PollerSet).filter(model.PollerSet.display_name==unicode(row[16])).first()
            if att.poller_set is None:
                obj.logger.info('PollerSet {} not found for {}, using default.'.format(row[16], att.display_name))
            sla = model.Sla.by_display_name(row[17])
            if sla is None:
                obj.logger.info('SLA {} not found for {}, using default.'.format(row[17], att.display_name))
                att.sla_id = 1
            else:
                att.sla_id = sla.id

            att.state = up_state
            model.DBSession.add(att)
            if att.attribute_type is not None:
                field_count += import_attribute_field(obj, att,row[0])
            model.DBSession.flush()
            attributes[row[0]] = att.id
            attribute_count += 1
    except IntegrityError as errmsg:
        obj.logger.error('Error importing attributes: %s', errmsg)
        transaction.abort()
        return None
    else:
        obj.logger.info('Attributes:  %d added.', attribute_count)
        obj.logger.info('Attribute Fields: %d added.', field_count)
    return attributes

def import_attribute_field(obj, attribute, old_att_id):
    field_count=0
    for field in attribute.attribute_type.fields:
        itf_name = field.tag
        # Exceptions/changes between them
        if itf_name == 'speed':
            itf_name = 'bandwidthin'
        row = obj.dbhandle.execute("""
            SELECT iv.value FROM interfaces_values iv,interface_types_fields itf
            WHERE iv.field=itf.id
            AND iv.interface=%s
            AND itf.name="%s" LIMIT 1""" % (old_att_id, itf_name)).first()
        if row is None:
            pass #logger.info('Tag %s for old ID %d not found in interface_values.', itf_name, old_att_id)
        else:
            af = model.AttributeField()
            af.attribute_id = attribute.id
            af.attribute_type_field = field
            af.value = row[0]
            model.DBSession.add(af)
            field_count += 1
    return field_count

def import_event(obj):
    add_count=0
    events = {}
    try:
        result = obj.dbhandle.execute('SELECT e.id,e.date, e.host, e.interface, e.state, e.username, e.info, e.referer, e.ack, e.analized, et.description FROM events e, types et WHERE e.type = et.id AND date > adddate(now(),-7) ORDER by e.id LIMIT 300')
        for row in result:
            event_type = model.EventType.by_name(unicode(row[10]))
            if event_type is None:
                event_type = model.EventType.by_id(1)
                obj.logger.warning('Event Type %s unable to be found by name.', row[10])
            ev = model.Event(event_type)
            ev.host_id = obj.host_id(row[2])
            ev.acknowledged = (row[8] == 1)
            ev.processed = (row[9] == 1)
            ev.created = row[1]
        
            # Interface could either be referencing a real attribute or
            # a field called that
            ev.attribute = DBSession.query(model.Attribute).filter(
                model.Attribute.host_id == ev.host_id).filter(
                model.Attribute.display_name == unicode(row[3])).first()
            if ev.attribute is None:
                interface_field= model.EventField('interface', unicode(row[3]))
                ev.fields.append(interface_field)
                DBSession.add(interface_field)
            
            # Alarm can be a state, or just a field called 'state'
            ev.event_state = model.EventState.by_name(unicode(row[4]))
            if ev.event_state is None:
                state_field = model.EventField('state', unicode(row[4]))
                ev.fields.append(state_field)
                DBSession.add(state_field)
            # username and info are just fields
            if row[5] != '':
                username_field = model.EventField('user', unicode(row[5]))
                ev.fields.append(username_field)
                DBSession.add(username_field)
            if row[6] != '':
                info_field = model.EventField('info', unicode(row[6]))
                ev.fields.append(info_field)
                DBSession.add(info_field)
            model.DBSession.add(ev)
            model.DBSession.flush()
            events[row[0]] = ev.id
            add_count += 1
    except IntegrityError as errmsg:
        obj.logger.error('Error importing events: %s', errmsg)
        transaction.abort()
        return None
    else:
        obj.logger.info('Events: %d added.', add_count)
    return events

def import_host(obj):
    add_count=0
    hosts = {}
    try:
        result = obj.dbhandle.execute('SELECT id,ip,name,rocommunity,rwcommunity,zone,tftp,autodiscovery,autodiscovery_default_customer,show_host,poll,creation_date,modification_date,last_poll_date,sysobjectid,config_type FROM hosts WHERE id>1 ORDER by id')
        for row in result:
            host = model.Host(mgmt_address=row[1],display_name=row[2])
            host.snmp_community_id = import_snmp(row[3],row[4])
            host.zone_id = obj.zone_id(row[5])
            host.tftp_server = row[6]
            host.autodiscovery_policy_id = row[7]
            host.default_user_id = obj.user_id(row[8])
            host.show_host = (row[9] == 1)
            host.pollable = (row[10] == 1)
            host.created = datetime.datetime.fromtimestamp(row[11])
            host.updated = datetime.datetime.fromtimestamp(row[12])
            host.discovered = datetime.datetime.now()
            host.next_discover = host.discovered + datetime.timedelta(minutes=30)
            host.sysobjid = row[14]
            host.config_transfer_id = row[15]

            DBSession.add(host)
            DBSession.flush()
            hosts[row[0]] = host.id
            add_count += 1

    except IntegrityError as errmsg:
        obj.logger.error('Error importing users: %s', errmsg)
        transaction.abort()
        return None
    else:
        obj.logger.info('Hosts: %d added.', add_count)
    return hosts

def import_hostconfig(obj):
    conf_count=0
    try:
        result = obj.dbhandle.execute("SELECT date,host,config FROM hosts_config WHERE id > 1 ORDER BY id")
        for row in result:
            conf = model.HostConfig()
            conf.created = datetime.datetime.fromtimestamp(row[0])
            conf.host_id = obj.host_id(row[1])
            conf.config = row[2]
            DBSession.add(conf)
            DBSession.flush()
    except IntegrityError as errmsg:
        obj.logger.error('Error importing host configs: %s', errmsg)
        transaction.abort()
        return None
    else:
        obj.logger.info('Hosts Config: %d added.', conf_count)
    return []

def import_interface(obj):
    add_count=0
    try:
        result = obj.dbhandle.execute('SELECT i.id,i.host,f.field,f.value FROM interfaces AS i, interfaces_values AS f WHERE i.type=4 and i.id=f.interface AND f.field IN (3,4,6)')
        ifaces={}
        for row in result:
            ifid = row[0]
            if ifid not in ifaces:
                ifaces[ifid] = model.Iface()
                ifaces[ifid].host_id = obj.host_id(row[1])
            if row[2] == 3:
                ifaces[ifid].ifindex = int(row[3])
            elif row[2] == 4:
                ifaces[ifid].display_name = unicode(row[3])
            elif row[2] == 6:
                ifaces[ifid].speed = int(row[3])
        for iface in ifaces.values():
            DBSession.add(iface)
            DBSession.flush()
            add_count += 1
    except IntegrityError as errmsg:
        obj.logger.error('Error importing interfaces: %s', errmsg)
        transaction.abort()
        return None
    else:
        obj.logger.info('Interfaces: %d added.', add_count)
    return []

def import_snmp(old_ro, old_rw):
    if old_ro is None:
        comm = model.SnmpCommunity.by_name(u'None')
        if comm is not None:
            return comm.id
    try:
        (ver,ro_comm) = old_ro.split(':')
        comm = DBSession.query(model.SnmpCommunity).filter(
            model.SnmpCommunity.readonly == [ver[1:],ro_comm]).first()
        if comm is not None:
            return comm.id
        comm = model.SnmpCommunity()
        comm.display_name = old_ro
        comm.readonly = [ver[1:],ro_comm]
        comm.trap = [ver[1:], ro_comm]
        DBSession.add(comm)
        DBSession.flush()
        return comm.id

    except:
            comm =  model.SnmpCommunity.by_name(u'None')
            if comm is not None:
                return comm.id
    return 1

def import_user(obj):
    """
    Users in JFFNMS become users  in RNMS
    """
    add_count=0
    users = {}
    result = obj.dbhandle.execute("SELECT id,username,name FROM clients WHERE id > 2 ORDER BY id")
    for row in result:
        user = model.User()
        user.user_name = unicode(row[1])
        user.display_name = unicode(row[2])
        user.email_address=unicode(row[1])
        user.password = u'password'
        try:
            DBSession.add(user)
            DBSession.flush()
        except IntegrityError as errmsg:
            obj.logger.error('Error importing users: %s', errmsg)
            transaction.abort()
            return None
        else:
            users[row[0]] = user.user_id
            add_count += 1
    obj.logger.info('Users: %d added.', add_count)
    return users

def import_zone(obj):
    add_count=0
    zones = {}
    try:
        result = obj.dbhandle.execute("SELECT id,zone,shortname,image,show_zone FROM zones WHERE id > 1 ORDER BY id")
        for row in result:
            #zone = model.Zone(display_name=row[1], short_name=row[2], icon=str(row[3]))
            zone = model.Zone(display_name=unicode(row[1]), short_name=unicode(row[2]), icon=row[3])
            zone.showable = (row[4] == 1)
            DBSession.add(zone)
            DBSession.flush()
            zones[row[0]] = zone.id
            add_count += 1
    except IntegrityError as errmsg:
        obj.logger.error('Error importing zones: %s', errmsg)
        transaction.abort()
        exit()
        return None
    else:
        obj.logger.info('Zones: %d added.', add_count)
    return zones
