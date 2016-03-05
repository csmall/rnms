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
""" Discover items from Compaq cpqmib """
from rnms.model import DiscoveredAttribute

def discover_cpqmib(dobj, att_type, host):
    """
    Discover one of the items from the cpqmib, the ad_parameter will have the
    key used to select which oids to use
    """
    try:
        mibinfo = cqpmib_oids[att_type.ad_parameters]
    except KeyError:
        return False
    return dobj.snmp_engine.get_table(
        host, mibinfo[1], mibinfo[0], 
        att_type=att_type, dobj=dobj)


def cb_cpqmib_phydrv(values, error, host, dobj, att_type):
    discovered_attributes = {}
    if values is not None:
        for row in values:
            controller = row[0]
            drive_index = row[1]
            drive_model = row[2]
            new_att = DiscoveredAttribute(host.id, att_type)
            new_att.display_name = 'Disk{}/{}'.format(controller, drive_index)
            new_att.index = '{}.{}'.format(controller, drive_index)
            new_att.set_field('controller', controller)
            new_att.set_field('drvindex', drive_index)
            new_att.set_field('model', drive_model)
            if row[3] != '2':
                new_att.oper_state = 'down'
            discovered_attributes[new_att.index] = new_att
    dobj.discover_callback(host.id, discovered_attributes)

def cb_cpqmib_fans(values, error, host, dobj, att_type):
    """ Callback function for CPQMIB fan status """

    discovered_attributes = {}
    if values is not None:
        for row in values:
            chassis = row[0]
            index = row[1]
            new_att = DiscoveredAttribute(host.id, att_type)
            new_att.display_name = 'Fan{}/{}'.format(chassis, index)
            new_att.index = '{}.{}'.format(chassis, index)
            new_att.set_field('chassis', chassis)
            new_att.set_field('fanindex', index)
            new_att.set_field('location', cpqmib_locations.get(row[2], u'Unknown'))
            if row[3] != '3':
                new_att.admin_state = 'down'
            if row[4] != '2':
                new_att.oper_state = 'down'
            discovered_attributes[new_att.index] = new_att
    dobj.discover_callback(host.id, discovered_attributes)

def cb_cpqmib_ps(values, error, host, dobj, att_type):
    """ Callback function for CPQMIB powersupply status """

    discovered_attributes = {}
    if values is not None:
        for row in values:
            chassis = row[0]
            index = row[1]
            new_att = DiscoveredAttribute(host.id, att_type)
            new_att.display_name = 'Power{}/{}'.format(chassis, index)
            new_att.index = '{}.{}'.format(chassis, index)
            new_att.set_field('chassis', chassis)
            new_att.set_field('bayindex', index)
            if row[3] != '3':
                new_att.admin_state = 'down'
            if row[4] != '2':
                new_att.oper_state = 'down'
            discovered_attributes[new_att.index] = new_att
    dobj.discover_callback(host.id, discovered_attributes)

def cb_cpqmib_temp(values, error, host, dobj, att_type):
    """ Callback function for CPQMIB temperature status """

    discovered_attributes = {}
    if values is not None:
        for row in values:
            chassis = row[0]
            index = row[1]
            new_att = DiscoveredAttribute(host.id, att_type)
            new_att.display_name = 'Temperature{}/{}'.format(chassis, index)
            new_att.index = '{}.{}'.format(chassis, index)
            new_att.set_field('chassis', chassis)
            new_att.set_field('tempindex', index)
            new_att.set_field('location', cpqmib_locations.get(row[2], u'Unknown'))
            if row[3] != '2':
                new_att.oper_state = 'down'
            discovered_attributes[new_att.index] = new_att
    dobj.discover_callback(host.id, discovered_attributes)
    
cqpmib_oids = {
        'phydrv': (cb_cpqmib_phydrv,(
            (1,3,6,1,4,1,232,3,2,5,1,1,1),
            (1,3,6,1,4,1,232,3,2,5,1,1,2),
            (1,3,6,1,4,1,232,3,2,5,1,1,3),
            (1,3,6,1,4,1,232,3,2,5,1,1,6),
            )),
        'fans': (cb_cpqmib_fans, (
            (1,3,6,1,4,1,232,6,2,6,7,1,1),
            (1,3,6,1,4,1,232,6,2,6,7,1,2),
            (1,3,6,1,4,1,232,6,2,6,7,1,3),
            (1,3,6,1,4,1,232,6,2,6,7,1,4),
            (1,3,6,1,4,1,232,6,2,6,7,1,9),
            )),
        'temperature': (cb_cpqmib_temp, (
            (1,3,6,1,4,1,232,6,2,6,8,1,1),
            (1,3,6,1,4,1,232,6,2,6,8,1,2),
            (1,3,6,1,4,1,232,6,2,6,8,1,3),
            (1,3,6,1,4,1,232,6,2,6,8,1,6),
            )),
        'powersupply': (cb_cpqmib_ps, (
            (1,3,6,1,4,1,232,6,2,9,3,1,1),
            (1,3,6,1,4,1,232,6,2,9,3,1,2),
            (1,3,6,1,4,1,232,6,2,9,3,1,3),
            (1,3,6,1,4,1,232,6,2,9,3,1,4),
            )),
        }

cpqmib_locations = {
        '1': u'other', '2': 'unknown', '3': 'system', '4': 'system board',
        '5': 'io board', '6': 'cpu', '7': 'memory', '8': 'storage',
        '9': 'removeable media', '10': 'power supply', '11': 'ambient',
        '12': 'chassis', '13': 'bridge card', 
        }


