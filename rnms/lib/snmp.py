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
#from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pyasn1.type import univ as pyasn_types
from pyasn1.type import tag

""" SNMP functions for rosenberg """

# Constants - used for oper and adminm statates
STATE_UP = 1
STATE_DOWN = 2
STATE_TESTING = 3
STATE_UNKNOWN = 4

DefaultSecurityName = 'Rosenberg'  # Arbitarily string really

def convert_value(raw_value):
    """
    Converts raw value from pysnmp library into something sensible to be
    used for the rest of the program. This is an ugly, ugly hack but seems
    to be the only wau to do it.
    """
    tag_format = raw_value.tagSet[0][1]
    tagid = raw_value.tagSet[0][2]
    if tag_format == tag.tagFormatSimple:
        if tagid in [1, 2, 0x0a]: # Boolean, Integer Enumerated
            return int(raw_value)
        if tagid in [3, 4, 5 ]: # BitString, OctectString Null
            return str(raw_value)

    # Default
    return raw_value.prettyOut(raw_value)
    

def _convert_host_community(host_community):
    """ Converts the (version,data) tuple into a format the SNMP library
    understands"""
    if host_community[0] == 1:
        return cmdgen.CommunityData(DefaultSecurityName, host_community[1],0)
    elif host_community[0] == 2:
        return cmdgen.CommunityData(DefaultSecurityName, host_community[1],1)
    elif host_community[0] == 3:
        return cmdgen.UsmUserData(host_community[2], host_community[3], host_community[4])
    return None

def get_int(host, oid,default=None):
    """ Return the integer value of the SNMP query for ''oid''."""
    raw_val = get(host, oid)
    if raw_val is None:
        return None
    return int(raw_val)

def get(host, oid, default=None):
    if host.community_ro is None:
        return default
    auth_data = _convert_host_community(host.community_ro)
    if auth_data is None:
        return default
    errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
            auth_data,
            cmdgen.UdpTransportTarget((host.mgmt_address, 161)), oid)
    if errorIndication is not None:
        # FIXME - log the error
        return default
    convert_value(varBinds[0][1])
    return varBinds[0][1].prettyOut(varBinds[0][1])

def walk(host,tableOID,rowCount=None,rowOID=None,keyColumn=None):
    """Either snmp walk or get bulk a SNMP table. the table will return a
    list of tuples where the key in the tuple is the sub-OID of the table

      host - the host object
      tableOID - OID of the table to be scanned

    rowCount - number of rows to get
    rowOID - OID that will return an integer for rowCount
    keyColumn - The slice from the OID that will be returned, if the value for
              this row is 1.2.5.2 and your keyColumn is 3 then 5 is the key
    """

    if host.community_ro is None:
        return None
    auth_data = _convert_host_community(host.community_ro)
    if auth_data is None:
        return None

    # If specified, get the size of the table
    maxRepetitions=50 # A guess
    if rowCount is not None:
        maxRepetitions=rowCount
    elif rowOID is not None:
        errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
                auth_data,
                cmdgen.UdpTransportTarget((host.mgmt_address, 161)), rowOID)
        if not errorIndication:
            maxRepetitions = int(varBinds[0][1])

    errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().bulkCmd(
            auth_data,
            cmdgen.UdpTransportTarget((host.mgmt_address, 161)), 0,maxRepetitions,tableOID)
    if errorIndication is not None:
        # FIXME - log the error
        return None
    retTable={}
    tableOIDlen=len(tableOID)
    for varBindRow in varBindTable:
        rowOID=varBindRow[0][0]
        if rowOID[:tableOIDlen] != tableOID:
            break
        if keyColumn is not None:
            if keyColumn > len(rowOID):
              keyColumn = -1
            tableIndex = str(rowOID[keyColumn])
        else:
            if len(rowOID) - tableOIDlen == 1:
                tableIndex = str(rowOID[-1])
            else:
                tableIndex = rowOID.prettyOut(rowOID[tableOIDlen:])
        retTable[tableIndex] = varBindRow[0][1].prettyOut(varBindRow[0][1])
    return retTable

