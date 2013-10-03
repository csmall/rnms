# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
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
# This attribute discovery module is based upon
# host_information.php from JFFNMS which was written by
# Copyright (C) <2002> Robert Bogdon  
# Copyright (C) <2002-2005> Modifications by Javier Szyszlican <javier@szysz.com>

#
""" Discover host system info via SNMP """
from rnms import model

def discover_host_information(dobj, att_type, host):
    """
    First find the sysObjectId to see if it is one we want
    """
    oid = (1,3,6,1,2,1,1,2,0)
    return dobj.snmp_engine.get_str(
        host, oid, cb_match_host,
        dobj=dobj, att_type=att_type)

def cb_match_host(value, error, dobj, att_type, host):
    """
    Given the returned sysObjectId, is it one we want and if so 
    set of another round of queries
    """
    if value is None:
        dobj.discover_callback(host.id, {})
        return
    match_sysobjs = att_type.ad_parameters.split(',')
    enterprise = unicode(value.replace('1.3.6.1.4.1.','',1))
    for match in match_sysobjs:
        if enterprise.find(match) == 0:
            break
    else:
        # Didnt match any of them
        dobj.discover_callback(host.id, {})
        return

    oids = (
            (1,3,6,1,2,1,1,1,0),
            (1,3,6,1,2,1,1,4,0),
            (1,3,6,1,2,1,1,5,0),
            (1,3,6,1,2,1,1,6,0),
            )
    dobj.snmp_engine.get_list(host, oids, cb_host_information, 
                              dobj=dobj, att_type=att_type)

def cb_host_information(values, error, dobj, host, att_type):
    if values is None:
        dobj.discover_callback(host.id, {})

    new_att = model.DiscoveredAttribute(host.id, att_type)
    new_att.display_name = u'CPU'
    new_att.index = '1'
    new_att.set_field('description', values[0])
    new_att.set_field('contact', values[1])
    new_att.set_field('name', values[2])
    new_att.set_field('location', values[3])

    # Walk the device table
    oid = (1,3,6,1,2,1,25,3,2,1,2)
    dobj.snmp_engine.get_many(host, (oid,), cb_host_devtable,
                               dobj=dobj, new_att=new_att)

def cb_host_devtable(values, error, dobj, host, new_att):
    num_cpu = 0
    if values is not None and len(values) > 0:
        for devtype in values[0]:
            if devtype == '1.3.6.1.2.1.25.3.1.3':
                num_cpu += 1
    if num_cpu == 0:
        num_cpu = 1
    new_att.set_field('cpu_num', num_cpu)
    dobj.discover_callback(host.id, {'1': new_att})
