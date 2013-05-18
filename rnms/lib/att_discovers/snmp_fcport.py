# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
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
"""
  Discover Fibre Channel ports through SNMP
  MIB: FIBRE-CHANNEL-FE-MIB
  RFC: 2837
"""

from rnms.lib import states
from rnms.model import DiscoveredAttribute

def discover_fc_ports(dobj, att_type, host):
    """
    Discover Fibre Channel ports using SNMP
    """
    oids = (
            (1,3,6,1,2,1,75,1,1,5,1,1), #fcFxPortIndex
            (1,3,6,1,2,1,75,1,1,5,1,2), #fcFxPortName
            (1,3,6,1,2,1,75,1,2,2,1,1), # admin status
            (1,3,6,1,2,1,75,1,2,2,1,2), # oper status
            )
    return dobj.snmp_engine.get_table(
        host, oids, cb_fc_ports, table_trim=1,
        host=host, dobj=dobj, att_type=att_type)

def cb_fc_ports(values, error, host, dobj, att_type):
    fc_ports = {}
    if values is None:
        dobj.discover_callback(host.id, fc_ports)
    for idx in values[0].values():
        new_port = DiscoveredAttribute(host.id, att_type)
        new_port.display_name = 'FC Port '+idx
        new_port.index = idx
        try:
            new_port.admin_state = fc_state(values[2][idx])
        except IndexError:
            pass
        try:
            new_port.oper_state = fc_state(values[3][idx])
        except IndexError:
            pass
        fc_ports[idx] = new_port
    dobj.discover_callback(host.id, fc_ports)


def fc_state(raw_value):
    if raw_value == '1':
        return states.STATE_UP
    elif raw_value == '3':
        return states.STATE_TESTING
    return states.STATE_DOWN

