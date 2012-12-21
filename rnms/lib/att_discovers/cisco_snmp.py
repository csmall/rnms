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
# Cisco envirommental and saagent discoveries based upon JFFNMS module which was
# Copyright (C) 2004 Anders Karlsson <anders.x.karlsson@songnetworks.se>
#
#
""" Cisco-specific attribute types using SNMP """
from rnms.lib import snmp
from rnms import model

def discover_cisco_envmib(host, **kw):
    """
    Walk the ifTable to find any SNMP interfaces
    """
    env_oid = (1,3,6,1,4,1,9,9,13,1)
    params =  kw['att_type'].ad_parameters.split(',')
    if len(params) != 3:
        return False
    name_base = params[0]
    oids = ( env_oid + tuple( int (x) for x in params[1].split('.')),
             env_oid + tuple( int (x) for x in params[2].split('.')),)

    return kw['dobj'].snmp_engine.get_table(host, oids, cb_cisco_envmib, table_trim=1, name_base=name_base, host=host, **kw)


def cb_cisco_envmib(values, error, host, dobj, name_base, **kw):
    env_items = {}

    if values is None:
        dobj.discover_callback(host.id, env_items)
        return

    for idx,name in values[0].items():
        new_att = model.DiscoveredAttribute(host.id, kw['att_type'])
        new_att.display_name = unicode(name_base + idx)
        new_att.index = idx
        try:
            oper = values[1][idx]
        except (KeyError, IndexError):
            pass
        else:
            if oper != '1':
                new_att.oper_status = 2
            if oper == '5':
                new_att.admin_status = 2
        env_items[idx] = new_att
    dobj.discover_callback(host.id, env_items)

def discover_cisco_saagent(host, **kw):
    """
    Walk the SA Agent table to find any relevant items
    Index is the rtr <num> number
    Description is tag <descr> under the rtr clause
    """
    oids =  ((1,3,6,1,4,1,9,9,42,1,5,2,1,1),
             (1,3,6,1,4,1,9,9,42,1,2,1,1,3),)
    return kw['dobj'].snmp_engine.get_table(host, oids, cb_cisco_saagent, table_trim=1, host=host, **kw)

def cb_cisco_saagent(values, error, host, dobj, **kw):
    saagents = {}

    if values is None:
        dobj.discover_callback(host.id, saagents)
        return
    for key,val in values[0].items():
        try:
            description = values[1][key]
        except (KeyError, IndexError):
            description = ''

        new_att = model.DiscoveredAttribute(host.id, kw['att_type'])
        new_att.display_name = unicode('SAA{} {}'.format(key, description))
        new_att.index = key
        saagents[key] = new_att
    dobj.discover_callback(host.id, saagents)

def discover_pix_connections(host, **kw):
    """
    Walk the PIX Connection table
    """
    oids = (
            (1,3,6,1,4,1,9,9,147,1,2,2,2,1,3),
            )
    return kw['dobj'].snmp_engine.get_table(host, oids, cb_pix_connections, table_trim=2, host=host, **kw)


def cb_pix_connections(values, error, host, dobj, att_type, **kw):
    conns = {}
    for key,descr in values[0]:
        new_att = model.DiscoveredAttribute(host.id, att_type)
        new_att.display_name = unicode('FW Stat{}'.format(key))
        new_att.index = key
        new_att.add_field('description', descr)
        conns[key] = new_att
    dobj.discover_callback(host.id, conns)

