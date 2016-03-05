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
""" SNMP attribute types autodiscovery """
from rnms.lib import snmp
from rnms import model

iftable_columns = {'2': 'descr', '5': 'speed', '7': 'admin', '8': 'oper'}


def discover_snmp_interfaces(dobj, att_type, host):
    """
    Walk the ifTable to find any SNMP interfaces
    """
    oids = ((1, 3, 6, 1, 2, 1, 2, 2, 1, 2),
            (1, 3, 6, 1, 2, 1, 2, 2, 1, 5),
            (1, 3, 6, 1, 2, 1, 2, 2, 1, 7),
            (1, 3, 6, 1, 2, 1, 2, 2, 1, 8),
            (1, 3, 6, 1, 2, 1, 4, 20, 1, 1),
            (1, 3, 6, 1, 2, 1, 4, 20, 1, 2),
            (1, 3, 6, 1, 2, 1, 4, 20, 1, 3),
            )
    return dobj.snmp_engine.get_many(
        host, oids, cb_snmp_interfaces, with_oid=1,
        dobj=dobj, att_type=att_type)


def cb_snmp_interfaces(values, error, host, dobj, att_type):
    if values is None or len(values[0]) == 0:
        dobj.discover_callback(host.id, {})
        return
    discovered_attributes = {}

    # Build the ifindex to ipaddr table
    ipaddrs = {}
    table_addrs = dict(values[4])
    table_masks = dict(values[6])
    for ipindex, ifindex in values[5]:
        ipaddrs[ifindex] = {}
        try:
            addr = table_addrs[ipindex]
        except KeyError:
            pass
        else:
            octects = addr.split('.')
            last_octect = int(octects[3])
            if last_octect % 2:
                last_octect += 1
            elif last_octect > 0:
                last_octect -= 1
            else:
                last_octect = 254
            ipaddrs[ifindex]['address'] = addr
            ipaddrs[ifindex]['peer'] =\
                '.'.join(octects[0:3]+[str(last_octect), ])
        try:
            ipaddrs[ifindex]['mask'] = table_masks[ipindex]
        except KeyError:
            pass

    ifspeeds = dict(values[1])
    for ifindex, ifdesc in values[0]:
        try:
            new_att = model.DiscoveredAttribute(host.id, att_type)
            new_att.display_name = ifdesc
            new_att.index = ifindex
        except IndexError:
            continue  # no name means we dont want it

        try:
            ifspeed = ifspeeds[ifindex]
        except KeyError:
            ifspeed = 100000000  #default is 100 Mbps
        new_att.set_field('speed', ifspeed)

#        try:
#            new_att.admin_state = state_name(values[3][ifindex])
#        except IndexError:
#            new_att.admin_state = 'down'
#        try:
##            new_att.oper_state = state_name(values[4][ifindex])
#        except IndexError:
#            new_att.oper_state = 'down'
        try:
            ipinfo = ipaddrs[ifindex]
        except KeyError:
            pass
        else:
            for k, v in ipinfo.items():
                new_att.set_field(k, v)
        discovered_attributes[unicode(ifindex)] = new_att
    dobj.discover_callback(host.id, discovered_attributes)


def discover_snmp_simple(dobj, att_type, host):
    """
    Check if the given OID exists and if so create the attribute
    Autodiscovery Parameters: <oid>|<display_name>
      oid: The SNMP OID to check
      display_name: Name of the attribute if we create it
    """
    try:
        tmpoid, display_name = att_type.ad_parameters.split('|')
        oid = tuple([int(x) for x in tmpoid.split('.')])
    except ValueError:
        return False
    return dobj.snmp_engine.get_one(host, oid, cb_snmp_simple,
                                    display_name=display_name,
                                    dobj=dobj,
                                    att_type=att_type,)


def cb_snmp_simple(values, error, host, dobj, att_type, display_name, **kw):
    if values is None:
        dobj.discover_callback(host.id, {})
        return
    new_att = model.DiscoveredAttribute(host.id, att_type)
    new_att.display_name = display_name
    new_att.index = 1
    dobj.discover_callback(host.id, {'1': new_att})
