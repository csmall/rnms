# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011 Craig Small <csmall@enc.com.au>
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
from rnms.lib import snmp
from pyasn1.type import univ as pyasn_types
from pyasn1.error import PyAsn1Error


def poll_snmpget(poller, attribute):
    """
    Generic SNMP get that is used for counters
    Returns: single value for the OID or None
    Parameters: the OID in dotted decimal e.g. '1.3.6.1.1.9'
    """
    try:
        oid = pyasn_types.ObjectIdentifier(poller.parameters)
    except PyAsn1Error:
        return None
    return snmp.get(attribute.host, tuple(oid))

