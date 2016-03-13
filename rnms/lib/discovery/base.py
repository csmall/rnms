# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2016 Craig Small <csmall@enc.com.au>
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

from sqlalchemy import and_

from rnms.model import DBSession, AttributeType

__all__ = ['BaseDiscover']


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
            if not dhost.cb_discovery_row(discovered_atts):
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
        if not self._force:
            conditions.append(AttributeType.ad_enabled == True)  # noqa
        atypes = DBSession.query(AttributeType).filter(and_(*conditions))
        for atype in atypes:
            self._attribute_types.append(atype)
            found_atypes.append(str(atype.id))

        if self._force and limit_atypes is not None:
            missing_atypes = set(limit_atypes).difference(set(found_atypes))
            if missing_atypes != set():
                print "Missing the following types: {}".format(
                    ','.join(missing_atypes))

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
