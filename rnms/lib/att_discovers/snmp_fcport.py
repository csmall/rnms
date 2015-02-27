# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
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

from rnms.model import DiscoveredAttribute


def discover_fc_ports(dobj, att_type, host):
    """
    Discover Fibre Channel ports using SNMP
    """
    oids = (
        (1, 3, 6, 1, 2, 1, 75, 1, 2, 2, 1, 1),  # admin status
        (1, 3, 6, 1, 2, 1, 75, 1, 2, 2, 1, 2),  # oper status
        )
    return dobj.snmp_engine.get_table(
        host, oids, cb_fc_ports, with_oid=1,
        dobj=dobj, att_type=att_type)


def cb_fc_ports(values, error, host, dobj, att_type):
    fc_ports = {}
    if values is None:
        dobj.discover_callback(host.id, fc_ports)
        return
    for ((idx, admin), (ign, oper)) in values:
        new_port = DiscoveredAttribute(host.id, att_type)
        new_port.display_name = 'FC Port '+idx
        new_port.index = idx
        new_port.admin_state = fc_state(admin)
        new_port.oper_state = fc_state(oper)
        fc_ports[idx] = new_port
    dobj.discover_callback(host.id, fc_ports)


def fc_state(raw_value):
    if raw_value == '1':
        return 'up'
    elif raw_value == '3':
        return 'testing'
    return 'down'
