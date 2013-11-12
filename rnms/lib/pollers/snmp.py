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

from pyasn1.type import univ as pyasn_types
from pyasn1.error import PyAsn1Error


def split_oid(params, host):
    """ Some devices have a second parameter which is the OID to use for
    SNMPv1 hosts
    """
    oids = params.split('|')
    if host.ro_community.is_snmpv1:
        try:
            return oids[1]
        except IndexError:
            pass
    return oids[0]


def parse_oid(raw_oid):
    if raw_oid == '':
        return None
    str_oid = str(raw_oid)
    if str_oid[0] == '.':
        str_oid = str_oid[1:]
    return pyasn_types.ObjectIdentifier().prettyIn(str_oid)


def poll_snmp_counter(poller_buffer, parsed_params, **kw):
    """
    SNMP get that returns an integer
    Parameters: <oid>|[snmpv1oid]
      oid: the OID in dotted decimal e.g. '1.3.6.1.1.9'
      snmpv1oid: if this exists and the host is using snmpv1 use this
                 oid instead
    """
    try:
        oid = parse_oid(split_oid(parsed_params, kw['attribute'].host))
    except PyAsn1Error:
        return False
    if oid is None:
        return False
    kw['pobj'].snmp_engine.get_int(
        kw['attribute'].host,
        oid, cb_snmp_counter, **kw)
    return True


def poll_snmp_counter_mul(poller_buffer, parsed_params, **kw):
    """
    SNMP get that returns an integer that is multiplier
    Parameters: <oid>|<multiplier>
      <oid>: the OID in dotted decimal e.g. '1.3.6.1.1.9'
      <multiplier>: value is multiplied by this
    """
    params = parsed_params.split('|')
    try:
        oid = parse_oid(params[0])
    except PyAsn1Error:
        return False
    if oid is None:
        return False
    try:
        f_mult = float(params[1])
    except (IndexError, ValueError, TypeError):
        return False
    kw['pobj'].snmp_engine.get_int(
        kw['attribute'].host, oid, cb_snmp_counter,
        multiplier=f_mult, **kw)
    return True


def cb_snmp_counter(value, error, pobj, attribute,
                    multiplier=None, **kw):
    if value is None:
        pobj.poller_callback(attribute.id, None)
        return
    if multiplier is not None:
        value = float(value) * float(multiplier)
    pobj.poller_callback(attribute.id, value)


def poll_snmp_status(poller_buffer, parsed_params, **kw):
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
    params = parsed_params.split('|')
    try:
        kw['mapping'] = params[1]
    except IndexError:
        return False
    try:
        kw['default_state'] = params[2]
    except IndexError:
        kw['default_state'] = None
    try:
        oid = parse_oid(params[0])
    except PyAsn1Error:
        return False

    if oid is None:
        return False
    return kw['pobj'].snmp_engine.get_str(kw['attribute'].host,
                                          oid, cb_snmp_status, **kw)


def cb_snmp_status(value, error, pobj, attribute, default_state, **kw):
    if value is None or error is not None:
        pobj.poller_callback(attribute.id, default_state)
        return
    try:
        for item in kw['mapping'].split(","):
            matchret = item.split("=")
            try:
                if value == matchret[0]:
                    retval = matchret[1]
                else:
                    continue
            except IndexError:
                pass
            else:
                pobj.poller_callback(attribute.id, retval)
                return
    except KeyError:
        pass
    pobj.poller_callback(attribute.id, default_state)


def poll_snmp_walk_average(poller_buffer, parsed_params, **kw):
    """
    Walk an entire table and average out the values across the table
    Parameters: the OID in dotted decimal e.g. '1.3.6.1.1.9'
    """
    if parsed_params == '':
        return False
    return kw['pobj'].snmp_engine.get_table(
        kw['attribute'].host,
        parsed_params, cb_snmp_walk_average, with_oid=1, **kw)


def cb_snmp_walk_average(values, error, pobj, attribute, **kw):
    """
    Returns: float average of the returned table
    """
    if values is None:
        pobj.poller_callback(attribute.id, None)
        return

    total = 0
    total_values = 0
    for value in values.values():
        try:
            total += float(value)
        except ValueError:
            pass
        else:
            total_values += 1

    if total_values == 0:
        average = None
    else:
        average = total / total_values
    pobj.poller_callback(attribute.id, average)
