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
"""
Index verification pollers
  The basic idea for all of these pollers is to scan some sort of SNMP
  table and find the item that matches some parameter of the attribute,
  usually the display_name. The poller then returns the discovered index
  to the backend, which updates or ignores it
"""

def filter_storage_name(value):
    """
    Change the raw storage name into something that makes sense and is
    consistent
    """
    junos_sep = value.find(', mounted on: ')
    if junos_sep >= 0:
        return value[junos_sep+14:]
    return value

def poll_verify_storage_index(poller_buffer, **kw):
    """
    Use a table of stroage indexes via SNMP to see if it has changed
    """
    oid = (1,3,6,1,2,1,25,2,3,1,3)
    if kw['attribute'].index == '':
        return False
    inst_oid = oid + (int(kw['attribute'].index),)

    kw['pobj'].snmp_engine.get_str(kw['attribute'].host, inst_oid, cb_storage_index, **kw)
    return True

def cb_storage_index(value, error, **kw):
    """
    Receives the name of the storage, should equal what we already have.
    If not, go find the new index
    """
    oid = (1,3,6,1,2,1,25,2,3,1,3)

    if value is None:
        kw['pobj'].poller_callback(kw['attribute'].id, kw['poller_row'], None)
        return
    value = filter_storage_name(value)
    if kw['attribute'].display_name == value:
        kw['pobj'].poller_callback(kw['attribute'].id, kw['poller_row'], kw['attribute'].index)
    else:
        kw['pobj'].snmp_engine.get_table(kw['attribute'].host, (oid,), cb_verify_storage_index, table_trim=1, **kw)


def cb_verify_storage_index(values, error, pobj, attribute, poller_row, **kw):
    """
    CallBack function for a snmp table
    the return functions in the PollerRow
    """

    if values is not None:
        for (inst, value) in values.items():
            value = filter_storage_name(value)
            if value == attribute.display_name:
                try:
                    pobj.poller_callback(attribute.id, poller_row, str(int(inst)))
                    return;
                except ValueError:
                    pass
    pobj.poller_callback(attribute.id, poller_row, None)


def poll_verify_interface_number(poller_buffer, **kw):
    """
    Use a table of ifIndex indexes via SNMP to see if it has changed
    """
    index = kw['attribute'].index
    if index is None or index == '':
        return False
    else:
        oid = (1,3,6,1,2,1,2,2,1,2)
        inst_oid = oid + (int(kw['attribute'].index),)
        kw['pobj'].snmp_engine.get_str(kw['attribute'].host, inst_oid, cb_interface_index, **kw)
    return True

def cb_interface_index(value, error, **kw):
    """
    Receives the name of the interface, should equal what we already have.
    If not, go find the new index
    """
    oid = (1,3,6,1,2,1,2,2,1,2)

    if value is not None and kw['attribute'].display_name == value:
        kw['pobj'].poller_callback(kw['attribute'].id, kw['poller_row'], kw['attribute'].index)
    else:
        kw['pobj'].snmp_engine.get_table(kw['attribute'].host, (oid,), cb_verify_interface_number, table_trim=1, **kw)

def cb_verify_interface_number(values, error, pobj, attribute, poller_row, **kw):
    """
    CallBack function for a snmp table
    the return functions in the PollerRow
    """

    if values is not None:
        for (inst, value) in values[0].items():
            if value == attribute.display_name:
                try:
                    pobj.poller_callback(attribute.id, poller_row, str(int(inst)))
                    return;
                except ValueError:
                    pass
    pobj.poller_callback(attribute.id, poller_row, None)

