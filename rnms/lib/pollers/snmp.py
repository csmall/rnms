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
import logging

from rnms.lib import snmp
from pyasn1.type import univ as pyasn_types
from pyasn1.error import PyAsn1Error

logger = logging.getLogger('pSNMP')

def parse_oid(raw_oid):
    str_oid = str(raw_oid)
    if str_oid[0] == '.':
        str_oid = str_oid[1:]
    try:
        oid = pyasn_types.ObjectIdentifier().prettyIn(str_oid)
    except PyAsn1Error as errmsg:
        logger.warning("OID \"%s\" could not be parsed: %s", str_oid, errmsg)
        return None
    return oid

def poll_snmp_counter(poller_buffer, parsed_params, **kw):
    """
    SNMP get that returns an integer
    Parameters: the OID in dotted decimal e.g. '1.3.6.1.1.9'
    """
    oid = parse_oid(parsed_params)
    if oid is None:
        return False
    kw['pobj'].snmp_engine.get_int(kw['attribute'].host, oid, cb_snmp_counter, **kw)
    return True

def poll_snmp_counter_mul(poller_buffer, parsed_params, **kw):
    """
    SNMP get that returns an integer that is multiplier
    Parameters: <oid>|<multiplier>
      <oid>: the OID in dotted decimal e.g. '1.3.6.1.1.9'
      <multiplier>: value is multiplied by this
    """
    params = parsed_params.split('|')
    oid = parse_oid(params[0])
    if oid is None:
        return False
    kw['pobj'].snmp_engine.get_int(kw['attribute'].host, oid, cb_snmp_counter, multiplier=int(params[1]), **kw)
    return True

def cb_snmp_counter(value, error, pobj, attribute, poller_row, multiplier=None, **kw):
    if error is not None:
        pobj.poller_callback(attribute.id, poller_row, None)
        return
    if multiplier is not None:
        value = value * multiplier
    pobj.poller_callback(attribute.id, poller_row, value)
        

def poll_snmp_status(poller_buffer, **kw):
    """
    Generic SNMP get that returns a status string
    Returns: a string based upon the SNMP value returned
    Parameters: <oid>|<val1>=<ret1>,...,<valN>=<retN>|<default ret>
    OID is in dotted decimal to get the value.
    The values are compared in the commar separated list and if
    a match return the corresponding ret
    An optional default return value can be used, returns None if
    there is an error
    """
    params = kw['parsed_params'].split('|')
    param_count = len(params)
    try:
        kw['mapping'] = params[1]
    except IndexError:
        pass
    try:
        kw['default_value'] = params[2]
    except IndexError:
        kw['default_value'] = None
    oid = parse_oid(params[0])
    if oid is None:
        return False
    kw['pobj'].snmp_engine.get_int(kw['attribute'].host, oid, cb_snmp_status, **kw)
    return True

def cb_snmp_status(value, error, pobj, attribute, poller_row, **kw):
    if error is not None:
        pobj.poller_callback(attribute.id, poller_row, kw['default_value'])
    try:
        for item in kw['mapping'].split(","):
            matchret = item.split("=")
            try:
                if value == int(matchret[0]):
                    pobj.poller_callback(attribute.id, poller_row, matchret[1])
                    return
            except IndexError:
                pass
    except KeyError:
        pass
    pobj.poller_callback(attribute.id, poller_row, kw['default_value'])


def poll_snmp_walk_average(poller_buffer, parsed_params, **kw):
    """
    Walk an entire table and average out the values across the table
    Parameters: the OID in dotted decimal e.g. '1.3.6.1.1.9'
    """
    if parsed_params == '':
        return False
    kw['pobj'].snmp_engine.get_table(kw['attribute'].host, parsed_params, cb_snmp_walk_average, table_trim=1, **kw)

def cb_snmp_walk_average(values, error, pobj, attribute, poller_row, **kw):
    """
    Returns: float average of the returned table
    """
    if values is None or len(values) == 0:
        pobj.poller_callback(attribute.id, poller_row, kw['default_value'])
        return

    total=0
    for value in values.values():
        try:
            total += float(value)
        except ValueError as errmsg:
            logger.error('Non-float value %s in snmp_walk_average()', value)
            pobj.poller_callback(attribute.id, poller_row, kw['default_value'])
            return
    pobj.poller_callback(attribute.id, poller_row, total/len(values))
