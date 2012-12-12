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
""" Discover items from Compaq cpqmib """
from rnms.lib import snmp
from rnms import model

def discover_cpqmib(host, **kw):
    """
    Discover one of the items from the cpqmib, the ad_parameter will have the
    key used to select which oids to use
    """
    try:
        mibinfo = cqpmib_oids[kw['att_type'].ad_parameters]
    except KeyError:
        return False
    return kw['dobj'].snmp_engine.get_table(host, mibinfo[1], mibinfo[0], table_trim=1, host=host, **kw)


def cb_cpqmib_phydrv(values, error, host, dobj, att_type, **kw):
    discovered_attributes = {}
    if values is not None:
        for key,controller in values[0].values():
            try:
                drive_index = values[1][key]
                drive_model = values[2][key]
                drive_status = values[3][key]
            except (KeyError, IndexError):
                pass
            else:
                new_att = mode.DiscoveredAttribute(host.id, att_type)
                new_att.display_name = 'Disk{}/{}'.format(controller, drive_index)
                new_att.index = '{}.{}'.format(controller, drive_index)
                new_att.set_field('controller', controller)
                new_att.set_field('drvindex', drive_index)
                new_att.set_field('model', drive_model)
                if drive_status != 2:
                    new_att.oper_state = 2
                discovered_attributes[new_att.index] = new_att
    dobj.discover_callback(host.id, discovered_attributes)

def cb_cpqmib_fans(values, error, host, dobj, att_type, **kw):
    """ Callback function for CPQMIB fan status """

    discovered_attributes = {}
    if values is not None:
        for key,chassis in values[0].values():
            try:
                index = values[1][key]
                loc_code = values[2][key]
                present = values[3][key]
                condition = values[4][key]
            except (KeyError, IndexError):
                pass
            else:
                new_att = mode.DiscoveredAttribute(host.id, att_type)
                new_att.display_name = 'Fan{}/{}'.format(chassis, index)
                new_att.index = '{}.{}'.format(chassis, index)
                new_att.set_field('chassis', chassis)
                new_att.set_field('fanindex', index)
                new_att.set_field('location', cpqmib_locations.get(loc_code, u'Unknown'))
                if present != 3:
                    new_att.admin_state = 2
                if status != 2:
                    new_att.oper_state = 2
                discovered_attributes[new_att.index] = new_att
    dobj.discover_callback(host.id, discovered_attributes)

def cb_cpqmib_ps(values, error, host, dobj, att_type, **kw):
    """ Callback function for CPQMIB powersupply status """

    discovered_attributes = {}
    if values is not None:
        for key,chassis in values[0].values():
            try:
                index = values[1][key]
                present = values[3][key]
                condition = values[4][key]
            except (KeyError, IndexError):
                pass
            else:
                new_att = mode.DiscoveredAttribute(host.id, att_type)
                new_att.display_name = 'Power{}/{}'.format(chassis, index)
                new_att.index = '{}.{}'.format(chassis, index)
                new_att.set_field('chassis', chassis)
                new_att.set_field('bayindex', index)
                if present != 3:
                    new_att.admin_state = 2
                if status != 2:
                    new_att.oper_state = 2
                discovered_attributes[new_att.index] = new_att
    dobj.discover_callback(host.id, discovered_attributes)

def cb_cpqmib_temp(values, error, host, dobj, att_type, **kw):
    """ Callback function for CPQMIB temperature status """

    discovered_attributes = {}
    if values is not None:
        for key,chassis in values[0].values():
            try:
                index = values[1][key]
                loc_code = values[2][key]
                condition = values[4][key]
            except (KeyError, IndexError):
                pass
            else:
                new_att = mode.DiscoveredAttribute(host.id, att_type)
                new_att.display_name = 'Temperature{}/{}'.format(chassis, index)
                new_att.index = '{}.{}'.format(chassis, index)
                new_att.set_field('chassis', chassis)
                new_att.set_field('tempindex', index)
                new_att.set_field('location', cqpmib_locations.get(loc_code, u'Unknown'))
                if status != 2:
                    new_att.oper_state = 2
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


