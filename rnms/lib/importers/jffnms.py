# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011 Craig Small <csmall@enc.com.au>
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
import re
import logging
from tg import config
from rnms import model
from rnms.model import DBSession
import transaction
from sqlalchemy.exc import IntegrityError
from datetime import date

class JffnmsConfig(object):
    """
    Configuration object for JFFNMS configurations.
    The object on creation needs to be given config_dir where the
    JFFNMS configuration files live.
    """
    def __init__(self, config_dir):
        self.config_values = {}
        self.config_dir = config_dir
        self._parse_default_file()
        self._parse_config_file()


    def _parse_default_file(self):
        default_re = re.compile('([a-z_]+):([a-z]+)\s+=\s+(\S.+)',re.IGNORECASE)
        default_file = file(self.config_dir + '/jffnms.conf.defaults','r')
        skip_config=None
        for line in default_file:
            result = default_re.match(line)
            if result:
                if len(result.groups()) != 3:
                    next
                (conf_key, conf_type, conf_value) = result.groups()
                if skip_config is not None and skip_config == conf_key:
                    next
                if conf_type in [ 'description', 'values' ] :
                    next
                elif conf_type == 'type':
                    if conf_value == 'phpmodule':
                        skip_config = conf_key
                    else:
                        skip_config = None
                    next
                elif conf_type == 'default':
                    self.config_values[conf_key] = conf_value.rstrip()
        default_file.close()

    def _parse_config_file(self):
        config_re = re.compile('([a-z_]+)\s+=\s+(\S.+)',re.IGNORECASE)
        config_file = file(self.config_dir + '/jffnms.conf','r')
        for line in config_file:
            result = config_re.match(line)
            if result:
                self.config_values[result.group(1)] = result.group(2).strip()
        config_file.close()

    def get(self, key):
        return self.config_values.get(key)


class JffnmsImporter(object):
    def __init__(self, dbhandle, verbose=True, commit=True, delete=False):
        self.dbhandle = dbhandle
        self.verbose=verbose
        self.commit = commit
        self.delete = delete
        self.zones = {}
        self.users = {}
        self.hosts = {}
        self.attributes = {}
        self.events = {}

    def do_import(self):
        """
        Start the JFFNMS importing process. Does not require any arguments.
        Returns False on failure.
        """
        importers = [ 'zones', 'users', 'hosts', 'interfaces', 'attributes',
                'events' ]
        for imp in importers:
            func = getattr(self, '_import_'+imp)
            if not callable(func):
                print "Function _import_%s is not callable." % imp
                return False
            if func() == False:
                return False

        if self.commit:
            transaction.commit()
            print 'All imports committed'
        else:
            transaction.abort()
            print 'All imports NOT committed'
        return True

    def _delete_all(self,del_model, del_name, del_id):
        if self.delete != True:
            return
        try:
            deleted_items = DBSession.query(del_model).filter(del_model.id>del_id).delete()
        except IntegrityError as err:
            print 'Error deleting %s: %s'  % (del_name,err)
        else:
            if self.verbose == True:
                print '%d %s pre-deleted.' % (deleted_items, del_name)

    def _import_zones(self):
        self._delete_all(model.Zone, 'Zones', 1)
        zone_count=0
        try:
            result = self.dbhandle.execute("SELECT id,zone,shortname,image,show_zone FROM zones WHERE id > 1 ORDER BY id")
            for row in result:
                #zone = model.Zone(display_name=row[1], short_name=row[2], icon=str(row[3]))
                zone = model.Zone(display_name=unicode(row[1]), short_name=unicode(row[2]), icon=row[3])
                zone.showable = (row[4] == 1)
                DBSession.add(zone)
                DBSession.flush()
                self.zones[row[0]] = zone.id
                zone_count += 1
        except IntegrityError as foo:
            print 'Error importing zones: %s'  % foo
            transaction.abort()
            return False
        else:
            if self.verbose:
                print 'Imported %d zones.' % zone_count
        return True

    def zone_id(self,jffnms_id):
        return self.zones.get(jffnms_id,1)

    def _import_users(self):
        if self.delete == True:
            try:
                deleted_users = DBSession.query(model.User).filter(model.User.user_id>2).delete()
            except IntegrityError as err:
                print 'Error deleting users: %s'  % err
            else:
                if self.verbose == True:
                    print '%d users pre-deleted.' % deleted_users
        user_count=0
        try:
            result = self.dbhandle.execute("SELECT id,username,name FROM clients WHERE id > 1 ORDER BY id")
            for row in result:
                user = model.User()
                user.user_name = unicode(row[1])
                user.display_name = unicode(row[2])
                user.email_address=unicode(row[1])
                user.password = u'password'
                DBSession.add(user)
                DBSession.flush()
                self.users[row[0]] = user.user_id
                user_count += 1
        except IntegrityError as err:
            print 'Error importing users: %s'  % err
            transaction.abort()
            return False
        else:
            if self.verbose:
                print 'Imported %d users.' % user_count
        return True

    def user_id(self,jffnms_id):
        return self.users.get(jffnms_id,1)

    @classmethod
    def import_snmp(self,old_comm):
        if old_comm is None:
            return None
        try:
            (ver,comm) = old_comm.split(':')
            return [ver, comm]
        except:
            return None

    def _import_hosts(self):
        result = self.dbhandle.execute('SELECT id,ip,name,rocommunity,rwcommunity,zone,tftp,autodiscovery,autodiscovery_default_customer,show_host,poll,creation_date,modification_date,last_poll_date,sysobjectid,config_type FROM hosts WHERE id>1 ORDER by id')
        for row in result:
            host = model.Host(mgmt_address=row[1],display_name=row[2])
            host.community_ro = self.import_snmp(row[3])
            host.zone_id = self.zone_id(row[5])
            host.tftp_server = row[6]
            host.autodiscovery_policy_id = row[7]
            host.default_user_id = self.user_id(row[8])
            host.show_host = (row[9] == 1)
            host.pollable = (row[10] == 1)
            host.created = date.fromtimestamp(row[11])
            host.updated = date.fromtimestamp(row[12])
            host.polled = date.fromtimestamp(row[13])
            host.sysobjid = row[14]
            host.config_transfer_id = row[15]

            DBSession.add(host)
            DBSession.flush()
            self.hosts[row[0]] = host.id

    def host_id(self,jffnms_id):
        return self.hosts.get(jffnms_id,1)


    def import_hostconfig(self):
        config_count=0
        result = self.dbhandle.execute("SELECT date,host,config FROM hosts_config WHERE id > 1 ORDER BY id")
        for row in result:
            conf = model.HostConfig()
            conf.created = date.fromtimestamp(row[0])
            conf.host_id = self.host_id(row[1])
            conf.config = row[2]
            DBSession.add(conf)
            DBSession.flush()
            conf_count += 1
            print 'Imported %d host configs.' % conf_count

    def get_interface_index(self,int_id):
        result = self.dbhandle.execute('SELECT interfaces_values.value from interfaces_values,interface_types_fields where interface=%d and interfaces_values.field=interface_types_fields.id AND interface_types_fields.ftype=3'%int_id)
        for row in result:
            return row[0]
        return ''

    def _import_interfaces(self):
        iface_count=0
        result = self.dbhandle.execute('SELECT i.id,i.host,f.field,f.value FROM interfaces AS i, interfaces_values AS f WHERE i.type=4 and i.id=f.interface AND f.field IN (3,4,6)')
        ifaces={}
        for row in result:
            ifid = row[0]
            if ifid not in ifaces:
                ifaces[ifid] = model.Iface()
                ifaces[ifid].host_id = self.host_id(row[1])
            if row[2] == 3:
                ifaces[ifid].ifindex = int(row[3])
            elif row[2] == 4:
                ifaces[ifid].display_name = unicode(row[3])
            elif row[2] == 6:
                ifaces[ifid].speed = int(row[3])
        for iface in ifaces.values():
            DBSession.add(iface)
            DBSession.flush()
            iface_count += 1
        if self.verbose:
            print 'Imported %d interfaces.' % iface_count
        return True

    def _import_attributes(self):
        self._delete_all(model.Attribute, 'Attributes', 1)
        #self._delete_all(model.AttributeField, 'AttributeFields', 0)
        attribute_count=0
        field_count=0
        result = self.dbhandle.execute('SELECT interfaces.*,interface_types.description as itype FROM interfaces,interface_types WHERE host > 1 AND interfaces.type=interface_types.id ORDER BY interfaces.id')
        for row in result:
            att = model.Attribute()
            att.display_name=unicode(row[2])
            att.host_id = self.hosts.get(row[3],1)
            att.index = self.get_interface_index(row[0])
            att.user_id = self.user_id(row[4])
            att.attribute_type = DBSession.query(model.AttributeType).filter(model.AttributeType.display_name==unicode(row[15])).first()
            #FIXME sla poll group
            att.make_sound = row[7]
            att.show_rootmap = row[8]
            att.created = date.fromtimestamp(row[10])
            att.updated = date.fromtimestamp(row[11])
            att.polled = date.fromtimestamp(row[12])
            model.DBSession.add(att)
            field_count += self._import_attribute_fields(att,row[0])
            model.DBSession.flush()
            self.attributes[row[0]] = att.id
            attribute_count += 1
        if self.verbose == True:
            print 'Imported %d attributes and %d fields.' % (attribute_count,field_count)
        return True

    def attribute_id(self,jffnms_id):
        return self.attributes.get(int(jffnms_id),1)

    def _import_attribute_fields(self, attribute, old_att_id):
        field_count=0
        for field in attribute.attribute_type.fields:
            result = self.dbhandle.execute("""
                SELECT iv.value FROM interfaces_values iv,interface_types_fields itf
                WHERE iv.field=itf.id
                AND iv.interface=%s
                AND itf.name="%s" LIMIT 1""" % (old_att_id, field.tag))
            if result is None:
                print 'Tag %s for old ID %d not found ininterface_values.' % (old_att_id, field.tag)
            for row in result:
                af = model.AttributeField()
                af.attribute_id = attribute.id
                af.attribute_type_field = field
                af.value = row[0]
                model.DBSession.add(af)
                field_count += 1
                break
        return field_count

    def _import_events(self):
        event_count=0
        result = self.dbhandle.execute('SELECT e.id,e.date, e.host, e.interface, e.state, e.username, e.info, e.referer, e.ack, e.analized, et.description FROM events e, types et WHERE e.type = et.id ORDER by e.id')
        for row in result:
            ev = model.Event()
            ev.host_id = self.host_id(row[2])
            #alarm_state_id
            ev.acknowledged = (row[8] == 1)
            ev.analyzed = (row[9] == 1)
            ev.created = row[1]
            ev.event_type = model.EventType.by_name(unicode(row[10]))
            if ev.event_type is None:
                ev.event_type = model.EventType.by_id(1)
                print(row[10])
                print('not foun')
            
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
            ev.alarm_state = model.AlarmState.by_name(unicode(row[4]))
            if ev.alarm_state is None:
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
            self.events[row[0]] = ev.id
            event_count += 1
        if self.verbose == True:
            print 'Imported %d Events.' % event_count
        return True
