# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012,2013 Craig Small <csmall@enc.com.au>
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
from rnms.model import AttributeField


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
    oid = (1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 3)
    if kw['attribute'].index == '':
        return False
    inst_oid = oid + (int(kw['attribute'].index),)

    kw['pobj'].snmp_engine.get_str(kw['attribute'].host, inst_oid,
                                   cb_storage_index, **kw)
    return True


def cb_storage_index(value, error, host, **kw):
    """
    Receives the name of the storage, should equal what we already have.
    If not, go find the new index
    """
    oid = (1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 3)

    if value is None:
        kw['pobj'].poller_callback(kw['attribute'].id, None)
        return
    value = filter_storage_name(value)
    if kw['attribute'].display_name == value:
        kw['pobj'].poller_callback(
            kw['attribute'].id, kw['attribute'].index)
    else:
        kw['pobj'].snmp_engine.get_table(host, (oid,), cb_verify_storage_index,
                                         with_oid=1, **kw)


def cb_verify_storage_index(values, error, pobj, attribute, **kw):
    """
    CallBack function for a snmp table
    the return functions in the PollerRow
    """

    if values is not None:
        for ((inst, value),) in values:
            value = filter_storage_name(value)
            if value == attribute.display_name:
                try:
                    pobj.poller_callback(
                        attribute.id, str(int(inst)))
                    return
                except ValueError:
                    pass
    pobj.poller_callback(attribute.id, None)


def poll_verify_interface_number(poller_buffer, **kw):
    """
    Use a table of ifIndex indexes via SNMP to see if it has changed
    """
    index = kw['attribute'].index
    if index is None or index == '':
        return False
    else:
        oid = (1, 3, 6, 1, 2, 1, 2, 2, 1, 2)
        inst_oid = oid + (int(kw['attribute'].index),)
        kw['pobj'].snmp_engine.get_str(
            kw['attribute'].host, inst_oid, cb_interface_index, **kw)
    return True


def cb_interface_index(value, error, host, **kw):
    """
    Receives the name of the interface, should equal what we already have.
    If not, go find the new index
    """
    oid = (1, 3, 6, 1, 2, 1, 2, 2, 1, 2)

    if value is not None and kw['attribute'].display_name == value:
        kw['pobj'].poller_callback(
            kw['attribute'].id, kw['attribute'].index)
    else:
        kw['pobj'].snmp_engine.get_table(
            host, (oid,), cb_verify_interface_number, with_oid=1, **kw)


def cb_verify_interface_number(values, error, pobj, attribute, **kw):
    """
    CallBack function for a snmp table
    the return functions in the PollerRow
    """

    if values is not None:
        for ((inst, value),) in values:
            if value == attribute.display_name:
                try:
                    pobj.poller_callback(attribute.id, str(int(inst)))
                    return
                except ValueError:
                    pass
    pobj.poller_callback(attribute.id, None)


def poll_verify_sensor_index(poller_buffer, **kw):
    """
    Check the index used for the sensor
    """
    base_oid = (1, 3, 6, 1, 4, 1, 2021, 13, 16)
    if kw['attribute'].index == '':
        return False
    tbl_idx = AttributeField.field_value(kw['attribute'].id, 'table_index')
    print tbl_idx
    inst_oid = base_oid + (int(tbl_idx), 1, 2,
                           int(kw['attribute'].get_field('row_index')))

    kw['pobj'].snmp_engine.get_str(kw['attribute'].host,
                                   inst_oid, cb_sensor_index, **kw)
    return True


def cb_sensor_index(value, error, host, **kw):
    """
    Receives the name of the sensor, should equal what we already have.
    If not, go find the new index
    """
    base_oid = (1, 3, 6, 1, 4, 1, 2021, 13, 16)
    table_oid = base_oid +\
        (int(kw['attribute'].get_field('table_index')), 1, 2)

    if value is None:
        kw['pobj'].poller_callback(kw['attribute'].id, None)
        return
    if kw['attribute'].display_name == value:
        kw['pobj'].poller_callback(kw['attribute'].id,
                                   kw['attribute'].index)
    else:
        kw['pobj'].snmp_engine.get_table(host, (table_oid,),
                                         cb_verify_sensor_index,
                                         with_oid=1, **kw)


def cb_verify_sensor_index(values, error, pobj, attribute, **kw):
    """
    CallBack function for a snmp table
    the return functions in the PollerRow
    """

    if values is not None:
        for ((inst, value),) in values:
            if value == attribute.display_name:
                try:
                    pobj.poller_callback(attribute.id,
                                         str(int(inst)))
                    return
                except ValueError:
                    pass
    pobj.poller_callback(attribute.id, None)
