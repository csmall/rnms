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
# This attribute discovery module is based upon
# host_information.php from JFFNMS which was written by
# Copyright (C) <2002> Robert Bogdon  
# Copyright (C) <2002-2005> Modifications by Javier Szyszlican <javier@szysz.com>

#
""" Discover host system info via SNMP """
from rnms.lib import snmp
from rnms import model

sys_fields = (('1','description'),
              ('4', 'contact'), 
              ('5', 'name'),
              ('6', 'location'),
              )

def discover_host_information(host, **kw):
    """
    First find the sysObjectId to see if it is one we want
    """
    oid = (1,3,6,1,2,1,1,2,0)
    kw['host']=host
    return kw['dobj'].snmp_engine.get_str(host, oid, cb_match_host, **kw)

def cb_match_host(value, error, **kw):
    """
    Given the returned sysObjectId, is it one we want and if so 
    set of another round of queries
    """
    if value is None:
        kw['dobj'].discover_callback(kw['host'].id, {})
        return
    match_sysobjs = kw['att_type'].ad_parameters.split(',')
    enterprise = unicode(value.replace('1.3.6.1.4.1.','',1))
    for match in match_sysobjs:
        if enterprise.find(match) == 0:
            break
    else:
        # Didnt match any of them
        kw['dobj'].discover_callback(kw['host'].id, {})
        return

    # Query for processor table and system info
    oids = (
            (1,3,6,1,2,1,1,1,0),
            (1,3,6,1,2,1,1,4,0),
            (1,3,6,1,2,1,1,5,0),
            (1,3,6,1,2,1,1,6,0),
            )
    req = snmp.SNMPRequest(kw['host'])
    req.set_replyall(True)
    req.oid_trim = 2
    for oid in oids:
        req.add_oid(oid, cb_host_information, data=kw)
    kw['dobj'].snmp_engine.get(req)

def cb_host_information(values, error, dobj, host, **kw):
    if values is None:
        dobj.discover_callback(host.id, {})

    new_att = model.DiscoveredAttribute(host.id, kw['att_type'])
    new_att.display_name = u'CPU'
    new_att.index = '1'
    new_att.set_field('contact', values['4.0'])
    new_att.set_field('name', values['5.0'])
    new_att.set_field('location', values['6.0'])
    dobj.discover_callback(host.id, {'1': new_att})



def host_count_cpus(hr_device_table):
    """
    Count the number of CPU devices found in the device table, or return
    the default of 1
    """
    cpu_count = 0
    for device in hr_device_table.values():
        if device.find('25.3.1.3'):
            cpu_count += 1
    if cpu_count == 0:
        cpu_count = 1
    return cpu_count
