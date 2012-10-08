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

def poll_verify_storage_index(poller_buffer, **kwargs):
    """
    Use a table of stroage indexes via SNMP to see if it has changed
    """
    oid = (1,3,6,1,2,1,25,2,3,1,3)

    kwargs['pobj'].snmp_engine.get_table(kwargs['attribute'].host, oid, cb_verify_storage_index, table_trim=1, kwargs=kwargs)
    return True

def cb_verify_storage_index(values, error, kwargs):
    """
    CallBack function for a snmp table
    the return functions in the PollerRow
    """

    for (inst, value) in values.items():
        junos_sep = value.find(', mounted on: ')
        if junos_sep >= 0:
            value = value[junos_sep+14:]
        if value == kwargs['attribute'].display_name:
            try:
                kwargs['pobj'].poller_callback(kwargs['attribute'], str(int(inst)))
                return;
            except ValueError:
                pass
    kwargs['pobj'].poller_callback(kwargs['attribute'], -1)


def poll_verify_interface_number(poller_buffer, **kwargs):
    """
    Use a table of ifIndex indexes via SNMP to see if it has changed
    """
    oid = (1,3,6,1,2,1,2,2,1,2)

    kwargs['pobj'].snmp_engine.get_table(kwargs['attribute'].host, oid, cb_verify_interface_number, table_trim=1, kwargs=kwargs)
    return True

def cb_verify_interface_number(values, error, kwargs):
    """
    CallBack function for a snmp table
    the return functions in the PollerRow
    """

    for (inst, value) in values.items():
        if value == kwargs['attribute'].display_name:
            try:
                kwargs['pobj'].poller_callback(kwargs['attribute'], str(int(inst)))
                return;
            except ValueError:
                pass
    kwargs['pobj'].poller_callback(kwargs['attribute'], -1)

