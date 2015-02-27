# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2013 Craig Small <csmall@enc.com.au>
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
Discover UPS devices and lines using either the standard or Mitsubishi MIB
  RFC: 1628
"""

from rnms import model

BATTERY_STATES = {
    '1': 'battery unknown', '2': 'battery normal',
    '3': 'battery low', '4': 'battery depleted'
    }


def discover_ups(dobj, att_type, host):
    """
    Discover a standard RFC 1628 UPS or Mitsubishi UPS using SNMP
    AD Parameters: none
    """
    oids = (
        (1, 3, 6, 1, 2, 1, 33, 1, 1, 5, 0),  # UPS-MIB:upsIdentName.0
        (1, 3, 6, 1, 2, 1, 33, 1, 2, 1, 0),  # UPS-MIB:upsBatteryStatus.0
        (1, 3, 6, 1, 4, 1, 13891, 101, 1, 5, 0),  # Mitsu ident
        (1, 3, 6, 1, 4, 1, 13891, 101, 2, 1, 0),  # Mitsu battery status
        )
    return dobj.snmp_engine.get_list(
        host, oids, cb_ups,
        dobj=dobj, att_type=att_type)


def cb_ups(values, error, host, dobj, att_type):
    if values is None:
        dobj.discover_callback(host.id, {})
    elif values[0] is not None:
        new_ups = model.DiscoveredAttribute(host.id, att_type)
        new_ups.display_name = u'UPS'
        new_ups.index = '1'
        new_ups.set_field('ident', values[0])
        new_ups.set_field('ups_oid', '1.3.6.1.2.1.33.1')
        new_ups.oper_state = BATTERY_STATES.get(values[1], 'unknown')
        dobj.discover_callback(host.id, {'1': new_ups})
    elif values[2] is not None:
        new_ups = model.DiscoveredAttribute(host.id, att_type)
        new_ups.display_name = u'UPS'
        new_ups.index = '1'
        new_ups.set_field('ident', values[2])
        new_ups.set_field('ups_oid', '1.3.6.1.4.1.13891.101')
        new_ups.oper_state = BATTERY_STATES.get(values[3], 'unknown')
        dobj.discover_callback(host.id, {'1': new_ups})
    else:
        dobj.discover_callback(host.id, {})


def discover_ups_lines(dobj, att_type, host):
    """
    Discover a standard RFC 1628 UPS or Mitsubishi UPS lines using SNMP
    AD Parameters: <oid>|<inout>|<add_index>
      oid: The OID of the table we use to query to find UPS lines
      inout: "in" or "out" for input or output lines respectively
      add_index: Add this value to index
    """
    params = att_type.ad_parameters.split('|')
    if len(params) != 3:
        return False
    try:
        oid = tuple([int(x) for x in params[0].split('.')])
    except ValueError:
        return False
    if params[1] not in ('in', 'out'):
        return False
    return dobj.snmp_engine.get_table(
        host, (oid,), cb_ups_lines,
        att_type=att_type, dobj=dobj,
        inout=params[1], add_index=int(params[2]))


def cb_ups_lines(values, error, host, dobj, att_type, **kw):
    ups_lines = {}
    if values is not None:
        for idx in values:
            new_line = model.DiscoveredAttribute(host.id, att_type)
            new_line.index = idx
            if kw['inout'] == 'in':
                new_line.display_name = u'Input Line {}'.format(idx)
            else:
                new_line.display_name = u'Output Line {}'.format(idx)
            new_line.add_field(
                'line_index',
                unicode(int(kw['add_index']) + int(idx)))
            ups_lines[idx] = new_line
    dobj.discover_callback(host.id, ups_lines)
