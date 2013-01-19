# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012 Craig Small <csmall@enc.com.au>
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
import logging
import datetime
import asyncore

from sqlalchemy import and_

from rnms import model
from rnms.lib.snmp import SNMPEngine
from rnms.lib import ntpclient
from rnms.lib.tcpclient import TCPClient
from rnms.lib.pingclient import PingClient
from rnms.lib.nmapclient import NmapClient


class AttDiscover(object):
    """
    Attribute Discovery object
    Can be given a host to scan or will scan all hosts looking for 
    new attributes
    """
    _print_only = True
    max_active_hosts = 5
    _force = False


    def __init__(self, hosts=None, print_only=True, force=False):
        self._active_hosts = {}
        self._waiting_hosts = []
        self.snmp_engine = SNMPEngine()
        self.ntp_client = ntpclient.NTPClient()
        self.tcp_client = TCPClient()
        self.ping_client = PingClient()
        self.nmap_client = NmapClient()
        self.logger = logging.getLogger("rnms")
        self._force = force

    def discover(self, limit_hosts=None, limit_atypes=None, print_only=True):
        """
        Run the discovery on either all hosts or the ones specified
        in this call. Returns the dictionary of hosts and found attributes
        """
        self._fill_host_table(limit_hosts)
        self._fill_attribute_type_table(limit_atypes)

        self.logger.debug('%d hosts requiring discovery.', len(self._waiting_hosts))
        while self._active_hosts != {} or self._waiting_hosts != []:
            num_active_hosts = len(self._active_hosts)
            if num_active_hosts < self.max_active_hosts:
                self._activate_hosts(self.max_active_hosts - num_active_hosts)
            self._check_active_hosts()

            # Check through all the engines and sockets
            host_count = len(self._active_hosts)
            need_asynpoll = False
            snmp_jobs = self.snmp_engine.poll()
            if snmp_jobs > 0:
                need_asynpoll = True
                host_count -= snmp_jobs
            nmap_jobs = self.nmap_client.poll()
            if nmap_jobs > 0:
                host_count -= nmap_jobs
            if self.ntp_client.poll():
                need_asynpoll = True
            if self.tcp_client.poll():
                need_asynpoll = True
            if need_asynpoll > 0:
                if nmap_jobs > 0:
                    asyncore.poll(0.1)
                else:
                    asyncore.poll(3.0)

            
    def discover_callback(self, host_id, discovered_atts):
        """
        All of the discovery plugins should call this method.
        Generally this is done with kw['dobj'].discover_callback(hid, atts)

        discovered_atts is a dictionary of index:DiscoveredAttribute 
        items that were discovered for this particular attribute type
        """
        try:
            active_host = self._active_hosts[host_id]
        except KeyError:
            self.logger.warning('H:%d Discover called back but host not found in active list.', host_id)
            return
        active_host['in_discovery'] = False
        host = active_host['host']
        attribute_type = active_host['attribute_type']

        known_atts = { att.index:att for att in host.attributes if att.attribute_type == attribute_type }
        unique_indexes = list(set(known_atts.keys() + discovered_atts.keys()))
        for idx in unique_indexes:
            self.logger.debug('H:%d AT:%d index:%s DB:%s HOST:%s', host_id, attribute_type.id, idx,
                    (known_atts[idx].display_name if idx in known_atts else 'Not found'),
                    (discovered_atts[idx].display_name if idx in discovered_atts else 'Not found')
                    )

            if idx not in known_atts:
                self._discovery_found(host, attribute_type, discovered_atts[idx])
            elif idx not in discovered_atts:
                self._discovery_lost(host, attribute_type, known_atts[idx])
            else:
                # We are in both
                self._discovery_validate(host, attribute_type, known_atts[idx], discovered_atts[idx])
                self._check_user(host, known_atts[idx])

    def _discovery_found(self, host, attribute_type, attribute):
        """
        Autodiscovery has found a new attribute that is not stored in 
        the database.
        """
        if host.autodiscovery_policy.can_add(attribute):
            self.logger.debug('H:%d AT:%d New Interface Found: %s', host.id, attribute_type.id, attribute.index)
        if host.autodiscovery_policy.permit_add:
            real_att = model.Attribute.from_discovered(host, attribute)
            model.DBSession.add(real_att)
            model.DBSession.flush()
            self.logger.debug('H:%d AT:%d Added %s = %d', host.id, attribute_type.id, attribute.index, real_att.id)

    def _discovery_lost(self, host, attribute_type, attribute):
        """
        Autodiscovery failed to find this attribute in the host but the
        database has this attribute.  Possibly delete or set disabled this
        Attribute.
        """
        # Host has this attribute but it wasn't discovered
        if attribute_type.ad_validate and attribute.poll_enabled:
            self.logger.debug('H:%d AT:%d Not found in host: %s', host.id, attribute_type.id, attribute.index)
            if host.autodiscovery_policy.can_del():
                model.DBSession.delete(attribute)
                event_info = u' - Deleted'
            elif host.autodiscovery_policy.can_disable():
                attribute.set_disabled()
                event_info = u' - Disabled'
            else:
                event_info = u''
            if host.autodiscovery_policy.alert_delete:
                new_event = model.Event.create_admin(host, attribute,
                        'Attribute not found in host{0}'.format(event_info))
                if new_event is not None:
                    model.DBSession.add(new_event)
                    new_event.process()

    def _discovery_validate(self, host, att_type, known_att, disc_att):
        """
        Autodiscovery has found an known Attribute.  If required this
        method will validate the fields to the latest values
        """
        changed_fields=[]
        if not att_type.ad_validate:
            return

        if known_att.display_name != disc_att.display_name[:known_att.display_name_len]:
            changed_fields.append("Display Name to \"{0}\" was \"{1}\"".format(disc_att.display_name, known_att.display_name))
            known_att.display_name = disc_att.display_name

        tracked_fields = [ (f.tag,f.display_name) for f in att_type.fields if f.tracked == True]
        for tag,fname  in tracked_fields:
            known_value = known_att.get_field(tag)
            disc_value = disc_att.get_field(tag)
            if known_value is not None and disc_value is not None and known_value != disc_value:
                changed_info = "{0} to \"{1}\" was \"{2}\"".format(fname, disc_value, known_value)
                self.logger.debug("H:%d A:%d Changed Field: %s", known_att.host.id, known_att.id, changed_info)
                changed_fields.append(changed_info)
                if host.autodiscovery_policy.permit_modify:
                    known_att.set_field(tag, disc_value)
        if changed_fields != []:
            new_event = model.Event.create_admin(host, known_att, 
                    'detected modification'+(', '.join(changed_fields)))
            if new_event is not None:
                model.DBSession.add(new_event)
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
            self._active_hosts[new_host.id] = {
                    'id': new_host.id,
                    'host': new_host,
                    'in_discovery': False,
                    'index': -1,
                    'attribute_type': None,
                    }
            new_count =- 1
            waiting_count =- 1

    def _fill_host_table(self, host_ids):
        """
        Add all or some hosts to the objects list that need
        autodiscovery run on them to find attributes
        """
        if host_ids is not None:
            assert(type(host_ids) == list)
            hosts = model.DBSession.query(model.Host).filter(model.Host.id.in_(host_ids))
        else:
            hosts = model.DBSession.query(model.Host).filter(model.Host.pollable == True)
        for host in hosts:
            self._waiting_hosts.append(host)

    def _fill_attribute_type_table(self, limit_atypes=None):
        """
        Cache the attribute type stuff once
        """
        found_atypes = []
        self._attribute_types = []
        conditions = []
        if limit_atypes is not None:
            conditions.append(model.AttributeType.id.in_(limit_atypes))
        if self._force == False:
            conditions.append(model.AttributeType.ad_enabled == True)
        atypes = model.DBSession.query(model.AttributeType).filter(and_(*conditions))
        for atype in atypes:
            self._attribute_types.append(atype)
            found_atypes.append(str(atype.id))

        if self._force == True and limit_atypes is not None:
            missing_atypes = set(limit_atypes).difference(set(found_atypes))
            if missing_atypes != set():
                print "Missing the following types: {}".format(','.join(missing_atypes))

    def _check_active_hosts(self):
        """
        Run through list of active hosts and start next discovery
        """
        for host_id,host in self._active_hosts.items():
            if host['in_discovery'] == True:
                continue
            if host['index'] == -1:
                self._check_sysobjid(host)
            else:
                self._run_discovery(host)
            host['index'] += 1
            
    def _run_discovery(self, host):
        """
        Run the discovery on this host
        """
        host['in_discovery'] = True
        host['start_time'] = datetime.datetime.now()
        attribute_type = self._get_discovery_row(host['index'])
        if attribute_type is None:
            self._finish_discovery(host)
            return
        host['attribute_type'] = attribute_type
        if attribute_type.autodiscover(self, host['host'], self._force) == False:
            # it failed so skip it
            host['in_discovery'] = False


    def _finish_discovery(self, host):
        del (self._active_hosts[host['id']])

    def _get_discovery_row(self, index):
        try:
            return self._attribute_types[index]
        except IndexError:
            return None

    def _check_sysobjid(self, host):
        """
        Check that the given host has a system.sysObjectID, if possible
        """
        if host['host'].sysobjid is not None and host['host'].sysobjid != '':
            return
        if  host['host'].community_ro is None:
            return

        host['in_discovery'] = True
        host['start_time'] = datetime.datetime.now()
        self.snmp_engine.get_str(host['host'], (1,3,6,1,2,1,1,2,0), self._cb_check_sysobjid, host_id=host['host'].id)

    def _cb_check_sysobjid(self, value, error, host_id):
        try:
            active_host = self._active_hosts[host_id]
        except KeyError:
            self.logger.warning('H:%d sysobjd Discover called back but host not found in active list.', host_id)
            return
        active_host['in_discovery'] = False
        if value is not None:
            new_sysobjid = value.replace('1.3.6.1.4.1','ent')
            active_host['host'].sysobjid = new_sysobjid

