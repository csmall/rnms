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

def poll_snmp_counter(poller_buffer, **kwargs):
    """
    SNMP get that returns an integer
    Parameters: the OID in dotted decimal e.g. '1.3.6.1.1.9'
    """
    str_oid = str(kwargs['parsed_params'])
    if str_oid[0] == '.':
        str_oid = str_oid[1:]
    try:
        oid = pyasn_types.ObjectIdentifier().prettyIn(str_oid)
    except PyAsn1Error as errmsg:
        logger.warning("A%d: OID \"%s\" could not be parsed: %s", kwargs['attribute'].id, str_oid, errmsg)
        return False
    kwargs['pobj'].snmp_engine.get_int(kwargs['attribute'].host, oid, cb_snmp_counter, kwargs=kwargs)
    return True

def poll_snmp_counter_mul(poller_buffer, **kwargs):
    """
    SNMP get that returns an integer that is multiplier
    Parameters: <oid>|<multiplier>
      <oid>: the OID in dotted decimal e.g. '1.3.6.1.1.9'
      <multiplier>: value is multiplied by this
    """
    params = kwargs['parsed_params'].split('|')
    str_oid = str(params[0])

    if str_oid[0] == '.':
        str_oid = str_oid[1:]
    try:
        oid = pyasn_types.ObjectIdentifier().prettyIn(str_oid)
    except PyAsn1Error as errmsg:
        logger.warning("A%d: OID \"%s\" could not be parsed: %s", kwargs['attribute'].id, str_oid, errmsg)
        return False
    kwargs['pobj'].snmp_engine.get_int(kwargs['attribute'].host, oid, cb_snmp_counter, kwargs=kwargs, multiplier=int(params[1]))
    return True

def cb_snmp_counter(value, error, kwargs, multiplier=None):
    if error is not None:
        kwargs['pobj'].poller_callback(kwargs['attribute'], None)
        return
    if multiplier is not None:
        value = value * multiplier
    kwargs['pobj'].poller_callback(kwargs['attribute'], value)
        

def poll_snmp_status(poller_buffer, **kwargs):
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
    params = kwargs['parsed_params'].split('|')
    param_count = len(params)
    try:
        kwargs['mapping'] = params[1]
    except IndexError:
        pass
    try:
        kwargs['default_value'] = params[2]
    except IndexError:
        kwargs['default_value'] = None
    try:
        oid = pyasn_types.ObjectIdentifier().prettyIn(str(params[0]))
    except PyAsn1Error as errmsg:
        logger.warning("A%d: OID \"%s\" could not be parsed: %s", kwargs['attribute'].id, params[0], errmsg)
        return False
    kwargs['pobj'].snmp_engine.get_int(kwargs['attribute'].host, oid, cb_snmp_status, kwargs=kwargs)
    return True

def cb_snmp_status(value, error, kwargs):
    if error is not None:
        kwargs['pobj'].poller_callback(kwargs['attribute'], kwargs['default_value'])
    try:
        for item in kwargs['mapping'].split(","):
            matchret = item.split("=")
            try:
                if value == int(matchret[0]):
                    kwargs['pobj'].poller_callback(kwargs['attribute'], matchret[1])
                    return
            except IndexError:
                pass
    except KeyError:
        pass
    kwargs['pobj'].poller_callback(kwargs['attribute'], kwargs['default_value'])


    
