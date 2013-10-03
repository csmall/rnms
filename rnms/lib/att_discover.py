# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012.2013 Craig Small <csmall@enc.com.au>
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
import datetime
import time
import transaction

from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from rnms.model import DBSession, Host, DiscoveryHost, Attribute,\
        AttributeType, Event

from rnms.lib.engine import RnmsEngine

SCAN_TABLE_SECONDS=300
DISCOVERY_TIMEOUT = 20

class BaseDiscover(object):
    """ Basic discovery class, used for both backend and frontend """
    NEED_CLIENTS = ('snmp', 'ntp', 'tcp', 'ping', 'nmap')
    _attribute_types = None
    _force = False

    def get_dhost(self, host_id):
        """ Get the DiscoveryHost given the host ID """
        raise NotImplemented

    def discover_callback(self, host_id, discovered_atts):
        """
        All of the discovery plugins should call this method.
        Generally this is done with kw['dobj'].discover_callback(hid, atts)

        discovered_atts is a dictionary of index:DiscoveredAttribute 
        items that were discovered for this particular attribute type
        """
        dhost = self.get_dhost(host_id)
        if dhost is not None:
            if dhost.cb_discovery_row(discovered_atts) == False:
                # We got to the end of the line
                self._finish_discovery(dhost)

    def fill_attribute_type_table(self, limit_atypes=None):
        """
        Cache the attribute type stuff once
        """
        found_atypes = []
        self._attribute_types = []
        conditions = []
        if limit_atypes is not None:
            conditions.append(AttributeType.id.in_(limit_atypes))
        if self._force == False:
            conditions.append(AttributeType.ad_enabled == True)
        atypes = DBSession.query(AttributeType).filter(and_(*conditions))
        for atype in atypes:
            self._attribute_types.append(atype)
            found_atypes.append(str(atype.id))

        if self._force == True and limit_atypes is not None:
            missing_atypes = set(limit_atypes).difference(set(found_atypes))
            if missing_atypes != set():
                print "Missing the following types: {}".format(','.join(missing_atypes))

    def get_discovery_row(self, index):
        try:
            return self._attribute_types[index]
        except IndexError:
            return None

    def cb_check_sysobjid(self, value, error, host):
        dhost = self.get_dhost(host.id)
        if dhost is not None:
            dhost.cb_check_sysobjid(value)

    def poll(self):
        """ Poll the engines used for discovery, """
        self.snmp_engine.poll()
        self.nmap_client.poll()
        self.ntp_client.poll()
        self.tcp_client.poll()
        return self.zmq_core.poll(0.1)

class AttDiscover(BaseDiscover, RnmsEngine):
    """
    Attribute Discovery object
    Can be given a host to scan or will scan all hosts looking for 
    new attributes
    """
    _print_only = True
    do_once = True
    max_active_hosts = 5
    scan_host_table_time = datetime.datetime.min

    _active_hosts = None
    _waiting_hosts = None



    def __init__(self, attribute_ids=None, host_ids=None, print_only=True, force=False, zmq_context=None, do_once=True):
        super(AttDiscover, self).__init__('adisc', zmq_context)

        self._active_hosts = {}
        self._waiting_hosts = []

        self._force = force
        self.do_once = do_once
        self.print_only = print_only

    def discover(self, limit_hosts=None, limit_atypes=None):
        """
        Run the discovery on either all hosts or the ones specified
        in this call. Returns the dictionary of hosts and found attributes
        """
        self.fill_attribute_type_table(limit_atypes)
        if self.do_once:
            self._fill_host_table(limit_hosts)
        while True:
            now = datetime.datetime.now()
            if not self.do_once and self.scan_host_table_time < now:
                self._fill_host_table(limit_hosts)
                self.scan_host_table_time = now + datetime.timedelta(seconds=SCAN_TABLE_SECONDS)

            num_active_hosts = len(self._active_hosts)
            if num_active_hosts < self.max_active_hosts:
                self._activate_hosts(self.max_active_hosts - num_active_hosts)

            # Check through all the engines and sockets
            #host_count = len(self._active_hosts)
            if self.poll() == False:
                return
            self._check_active_hosts()
            if self._active_hosts == {} and self._waiting_hosts == []:
                # No more hosts to check
                # sleep until we need more things to do 
                if self.do_once == True or self.end_thread == True:
                    break
                transaction.commit()
                if self._sleep_until_next() == False:
                    return
        # Done, lets get out of here
        transaction.commit()

    def get_dhost(self, host_id):
        try:
            return self._active_hosts[host_id]
        except KeyError:
            self.logger.warning('H:%d Discover called back but host not found in active list.', host_id)
        return None

    def _discovery_found(self, host, atype_id, attribute):
        """
        Autodiscovery has found a new attribute that is not stored in 
        the database.
        """
        if host.autodiscovery_policy.can_add(attribute):
            self.logger.debug('H:%d AT:%d New Interface Found: %s',
                              host.id, atype_id, attribute.index)
        if host.autodiscovery_policy.permit_add:
            if self.print_only:
                self.logger.debug('H:%d AT:%d Added %s',
                                host.id, atype_id, attribute.index)
            else:
                real_att = Attribute.from_discovered(host, attribute)
                DBSession.add(real_att)
                DBSession.flush()
                self.logger.debug('H:%d AT:%d Added %s = %d',
                                  host.id, atype_id, attribute.index,
                                  real_att.id)

    def _discovery_lost(self, host, attribute):
        """
        Autodiscovery failed to find this attribute in the host but the
        database has this attribute.  Possibly delete or set disabled this
        Attribute.
        """
        # Host has this attribute but it wasn't discovered
        if attribute.attribute_type.ad_validate and attribute.poll_enabled:
            self.logger.debug('H:%d AT:%d Not found in host: %s',
                              host.id, attribute.attribute_type_id,
                              attribute.index)
            if host.autodiscovery_policy.can_del():
                if self.print_only:
                    DBSession.delete(attribute)
                event_info = u' - Deleted'
            elif host.autodiscovery_policy.can_disable():
                if self.print_only:
                    attribute.set_disabled()
                event_info = u' - Disabled'
            else:
                event_info = u''
            if host.autodiscovery_policy.alert_delete and not self.print_only:
                new_event = Event.create_admin(host, attribute,
                        'Attribute not found in host{0}'.format(event_info))
                if new_event is not None:
                    DBSession.add(new_event)
                    new_event.process()

    def _discovery_validate(self, host, known_att, disc_att):
        """
        Autodiscovery has found an known Attribute.  If required this
        method will validate the fields to the latest values
        """
        changed_fields=[]
        if not known_att.attribute_type.ad_validate:
            return

        if known_att.display_name != disc_att.display_name[:known_att.display_name_len]:
            changed_fields.append("Display Name to \"{0}\" was \"{1}\"".format(disc_att.display_name, known_att.display_name))
            if self.print_only:
                known_att.display_name = disc_att.display_name

        tracked_fields = [ (f.tag,f.display_name)
                          for f in known_att.attribute_type.fields if f.tracked == True]
        for tag,fname  in tracked_fields:
            known_value = known_att.get_field(tag)
            disc_value = disc_att.get_field(tag)
            if known_value is not None and disc_value is not None and known_value != disc_value:
                changed_info = "{0} to \"{1}\" was \"{2}\"".format(fname, disc_value, known_value)
                self.logger.debug("H:%d A:%d Changed Field: %s", known_att.host.id, known_att.id, changed_info)
                changed_fields.append(changed_info)
                if host.autodiscovery_policy.permit_modify and \
                   not self.print_only:
                    known_att.set_field(tag, disc_value)
        if not self.print_only and changed_fields != []:
            new_event = Event.create_admin(host, known_att, 
                    'detected modification'+(', '.join(changed_fields)))
            if new_event is not None:
                DBSession.add(new_event)
                new_event.process()

    def _check_user(self, host, attribute):
        """
        Check that there is a valid user assigned to this attribute and
        report if it is not
        """
        if attribute.user_id == 1:
            pass #FIXME need to fix the customer/client/user stuff in attributes

    def _activate_hosts(self, new_count):
        """
        Move hosts from the waiting queue to the active queue
        """
        waiting_count = len(self._waiting_hosts)
        while new_count >  0 and waiting_count > 0:
            new_host = self._waiting_hosts.pop()
            self._active_hosts[new_host.id] = new_host
            new_count =- 1
            waiting_count =- 1
            if new_host.start_discovery(self.cb_check_sysobjid) == False:
                self._finish_discovery(new_host)

    def _fill_host_table(self, host_ids):
        """
        Add all or some hosts to the objects list that need
        autodiscovery run on them to find attributes
        """
        conditions = [Host.id > 1]
        if host_ids is not None:
            assert(type(host_ids) == list)
            conditions.append(Host.id.in_(host_ids))
        else:
            conditions.append(Host.pollable == True)
        
        hosts = DBSession.query(Host).options(
            joinedload(Host.autodiscovery_policy),
            joinedload(Host.ro_community)).filter(
                and_(*conditions))
        for host in hosts:
            self._waiting_hosts.append(DiscoveryHost(self, host))

    def _finish_discovery(self, dhost):
        """
        This method is called once we have finished discovering all
        Attribute Types for this Host.
        """
        del (self._active_hosts[dhost.id])

        for atype_id,discovered_attributes in \
                                              dhost.discovered_attributes.items():
            self.check_attributes(dhost.obj, atype_id, discovered_attributes)


    def check_attributes(self, host, atype_id, discovered_atts):
        """ We have a list of discovered attributes for a particular
        attribute type. Match them with the known set
        """
        known_atts = self._get_host_attributes(host.id, atype_id)
        unique_indexes = list(set(known_atts.keys() + discovered_atts.keys()))
        for idx in unique_indexes:
            self.logger.debug('H:%d AT:%d index:%s DB:%s HOST:%s',
                              host.id, atype_id, idx,
                              (known_atts[idx].display_name
                               if idx in known_atts else 'Not found'),
                              (discovered_atts[idx].display_name
                               if idx in discovered_atts else 'Not found')
                    )

            if idx not in known_atts:
                self._discovery_found(host, atype_id, discovered_atts[idx])
            elif idx not in discovered_atts:
                self._discovery_lost(host, known_atts[idx])
            else:
                # We are in both
                self._discovery_validate(host, known_atts[idx], discovered_atts[idx])
                self._check_user(host, known_atts[idx])



    def _get_host_attributes(self, host_id, atype_id):
        """ Return a list of Attributes for the given hosts for a given
        AttributeType """
        atts = DBSession.query(Attribute).filter(and_(
            Attribute.host_id == host_id,
            Attribute.attribute_type_id == atype_id))
        if atts is None:
            return {}
        return { att.index:att for att in atts}

    def _check_active_hosts(self):
        """ Go through list of active hosts to see if any have taken too
        long to poll """
        timeout_time = time.time() - DISCOVERY_TIMEOUT
        for host_id, dhost in self._active_hosts.items():
            if dhost.in_discovery == False:
                continue
            if dhost.start_time < timeout_time:
                self.logger.notice('H:%d AT:%d Discovery Timeout',
                                   dhost.id, dhost.attribute_type.id)
                if dhost.cb_discovery_row(None) == False:
                    self._finish_discovery(dhost)

    def _sleep_until_next(self):
        """ Stay in this loop until we need to scan more hosts """
        next_host = Host.next_autodiscover()
        if next_host is None:
            return self.sleep(self.scan_host_table_time)
        else:
            self.logger.info('Next atribute discovery #%d at %s', next_host.id, next_host.next_discover.ctime())
            return self.sleep(min(next_host.next_discover, self.scan_host_table_time))

class SingleDiscover(BaseDiscover, RnmsEngine):
    """ Discover a single host. Used for the web frontend
    sd = SingleDiscover('att_disc')
    sd.discover(Host.by_id('42'))
    """
    discovered_atts = None
    combined_atts = None

    def discover(self, host):
        self.do_poll = True
        self.fill_attribute_type_table()
        self.dhost = DiscoveryHost(self, host)
        if self.dhost.start_discovery(self.cb_check_sysobjid) == False:
            self._finish_discovery(self.dhost)
        while self.do_poll:
            if self.poll() == False:
                break

    def get_dhost(self, host_id):
        return self.dhost

    def _get_host_attributes(self):
        host_atts = {}
        atts = DBSession.query(Attribute).filter(
            Attribute.host_id == self.dhost.id)
        for att in atts:
            if att.attribute_type_id not in host_atts:
                host_atts[att.attribute_type_id] = {}
            host_atts[att.attribute_type_id][att.index] = att
        return host_atts

    def _finish_discovery(self, dhost):
        self.combined_atts = {}
        self.do_poll = False
        known_atts = self._get_host_attributes()
        self.discovered_atts = {k:v for k,v in dhost.discovered_attributes.items()
                           if v != {}}
        atype_ids = list(set(known_atts.keys() +
                         self.discovered_atts.keys()))
        atype_ids.sort()
        for atype_id in atype_ids:
            try:
                self.combined_atts[atype_id] = self.discovered_atts[atype_id]
            except KeyError:
                self.combined_atts[atype_id] = {}
            try:
                self.combined_atts[atype_id].update(known_atts[atype_id])
            except KeyError:
                pass



