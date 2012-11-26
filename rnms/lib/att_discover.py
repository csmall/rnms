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
from rnms.lib.snmp import SNMPEngine, SNMPRequest
from rnms.lib import ntpclient
from rnms.lib.tcpclient import TCPClient
from rnms.lib.pingclient import PingClient


class AttDiscover(object):
    """
    Attribute Discovery object
    Can be given a host to scan or will scan all hosts looking for 
    new attributes
    """
    _print_only = True
    max_active_hosts = 5


    def __init__(self, hosts=None, print_only=True):
        self._active_hosts = {}
        self._waiting_hosts = []
        self.snmp_engine = SNMPEngine()
        self.ntp_client = ntpclient.NTPClient()
        self.tcp_client = TCPClient()
        self.ping_client = PingClient()
        self.logger = logging.getLogger("aad")

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
            if self.ntp_client.poll():
                need_asynpoll = True
            if self.tcp_client.poll():
                need_asynpoll = True
            if need_asynpoll > 0:
                if host_count > 0:
                    asyncore.poll(0.1)
                else:
                    asyncore.poll(3.0)
                polls_running = True

            
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
            self.logger.warning('H:%d - Discover called back but host not found in active list.', host_id)
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
                # We have discovered an attribute that is not previously
                # known
                if host.autodiscovery_policy.can_add(discovered_atts[idx]) :
                    self.logger.debug('H:%d AT:%d index:%s - New Interface Found', host_id, attribute_type.id, idx)
                if host.autodiscovery_policy.permit_add:
                    real_att = model.Attribute.from_discovered(discovered_atts[idx], host.autodiscovery_policy)
                    




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
                    'index': 0,
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
        self._attribute_types = []
        if limit_atypes is None:
            atypes = model.DBSession.query(model.AttributeType).filter(model.AttributeType.ad_enabled == True)
        else:
            atypes = model.DBSession.query(model.AttributeType).filter(and_(model.AttributeType.ad_enabled == True, model.AttributeType.id.in_(limit_atypes)))
        for atype in atypes:
            self._attribute_types.append(atype)


    def _check_active_hosts(self):
        """
        Run through list of active hosts and start next discovery
        """
        for host_id,host in self._active_hosts.items():
            if host['in_discovery'] == True:
                continue
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
        if attribute_type.autodiscover(self, host['host']) == False:
            # it failed so skip it
            host['in_discovery'] = False


    def _finish_discovery(self, host):
        del (self._active_hosts[host['id']])

    def _get_discovery_row(self, index):
        try:
            return self._attribute_types[index]
        except IndexError:
            return None
