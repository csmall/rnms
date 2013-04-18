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
""" Discover storage items via SNMP """
from rnms import model

# Device names we ignore
blocked_device_names = ('/dev', '/.vol', )

storage_device_types = {
        '1': u'Other',
        '2': u'Ram',
        '3': u'VirtualMemory',
        '4': u'FixedDisk',
        '5': u'RemovableDisk',
        '6': u'FloppyDisk',
        '7': u'CompactDisk',
        '8': u'RamDisk',
        }

def discover_storage(host, **kw):
    """
    Walk the hrStorageTable to find any storage items
    """
    oids = ((1,3,6,1,2,1,25,2,3,1,1),
            (1,3,6,1,2,1,25,2,3,1,2),
            (1,3,6,1,2,1,25,2,3,1,3),
            (1,3,6,1,2,1,25,2,3,1,4),
            (1,3,6,1,2,1,25,2,3,1,5),
            )

    return kw['dobj'].snmp_engine.get_table(host, oids, cb_storage, table_trim=1, host=host, **kw)

def cb_storage(values, error, host, dobj, **kw):
    if values is None:
        dobj.discover_callback(host.id, {})
        return
    discovered_attributes = {}

    for sidx in values[0]:
        try:
            descr = storage_parse_description(values[2][sidx])
        except IndexError:
            continue

        if descr in blocked_device_names:
            continue

        new_att = model.DiscoveredAttribute(host.id, kw['att_type'])
        new_att.display_name = descr
        new_att.index = sidx
        try:
            type_index = values[1][sidx]
        except IndexError:
            new_att.set_field('storage_type', u'Other')
        else:
            new_att.set_field('storage_type', storage_get_device_type(type_index))

        try:
            block_size = int(values[3][sidx])
            block_count = int(values[4][sidx])
        except (IndexError, ValueError):
            new_att.set_field('size', 0)
        else:
            new_att.set_field('size', block_size * block_count)
        discovered_attributes[unicode(sidx)] = new_att
    dobj.discover_callback(host.id, discovered_attributes)


def storage_get_device_type(typeoid):
    """
    Returns the textual representation of the storage device type
    """
    try:
        return storage_device_types[typeoid.split('.')[-1]]
    except KeyError:
        return u'Other'

def storage_parse_description(raw_desc):
    """
    Fix the description by stripping some components out of it
    Returns filtered description
    """

    # Junos has the interface name 
    offset =  raw_desc.find('mounted on: ')
    if offset > 0:
        return raw_desc[offset+len('mounted on: '):]

    return raw_desc
