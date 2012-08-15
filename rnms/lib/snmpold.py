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

# import for SNMP engine
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from asyncore import poll
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
from time import time

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

class SnmpEngine():
    """ 
    This class does all the heavy lifting work to produce an asynchronous
    SNMP engine.  Pollers submit their requests to it with a call back
    that gets the result.

    callback functions expect (result, host, kwargs). the kwargs are
    anything extra sent to the inital function.
    """
    requests = {}
    proto_mods = {}
    default_timeout = 3 # number of seconds before item is considered gone

    def __init__(self):
        self.dispatcher = AsynsockDispatcher()
        self.dispatcher.registerTransport(
                udp.domainName, udp.UdpSocketTransport().openClientMode()
                )
        self.dispatcher.registerRecvCbFun(self._receive_msg)

    def _pmod_from_community(self, community):
        """
        Returns the Proto Module based upon the SNMP community structure
        """
        version = community[0]
        if version == 1:
            return api.protoModules[api.protoVersion1]
        elif version == 2:
            return api.protoModules[api.protoVersion2c]
        return None

    def _pmod_from_api(self, api_version):
        if api_version in api.protoModules:
            return api.protoModules[api_version]
        return None

    def socketmap(self):
        """ Returns the socket of the transportDispatcher """
        return self.dispatcher.getSocketMap()

    def poll(self):
        """
        Run through all the requests and check timeout of all pending
        requests. Returns true if there is still things to do
        """
        poll(0.2, self.dispatcher.getSocketMap())
        return self._requests_pending() or self.dispatcher.jobsArePending() or self.dispatcher.transportsAreWorking()

    def _add_request(self, reqid, cb_func, host, default ,kwargs):
        self.requests[reqid] = {
                'cb_func': cb_func,
                'host': host,
                'default': default,
                'kwargs': kwargs }

    def _get_request(self, reqid):
        return self.requests.get(reqid, None)

    def _del_request(self, reqid):
        try:
            del(self.requests[reqid])
        except KeyError:
            pass

    def _requests_pending(self):
        return len(self.requests) > 0

    def _receive_msg(self, dispatcher, trans_domain, trans_address, msg):
        pmod = self._pmod_from_api(api.decodeMessageVersion(msg))
        if pmod is None:
            # FIXME logging
            print "Cannot find pmod"
            return
        while msg:
            rcv_msg, msg = decoder.decode(msg, asn1Spec=pmod.Message())
        rcv_pdu = pmod.apiMessage.getPDU(rcv_msg)
        request_id = pmod.apiPDU.getRequestID(rcv_pdu)
        request = self._get_request(request_id)
        if request is None:
            return
        # Check for error
        error_status = pmod.apiPDU.getErrorStatus(rcv_pdu)
        if error_status:
            request['cb_func'](request['default'], request['host'], request['kwargs'], error=error_status.prettyPrint())
        else:
            varbinds = {}
            for oid, val in pmod.apiPDU.getVarBinds(rcv_pdu):
                varbinds[oid.prettyPrint()] = val.prettyPrint()
            if len(varbinds) > 0:
                request['cb_func'](varbinds, request['host'], request['kwargs'])
            else:
                request['cb_func'](request['default'], request['host'], request['kwargs'])
        self._del_request(request_id)
        #self.dispatcher.jobFinished(1)

    def is_busy(self):
        """ Are there either jobs that are waiting or requests that are
        pending within the engine?
        """
        return self.dispatcher.jobsArePending() or self.dispatcher.transportsAreWorking()

    def _build_message(self, community, oid):
        pmod = self._pmod_from_community(community)
        if pmod is None:
            return None,None
        pdu = pmod.GetRequestPDU()
        pmod.apiPDU.setDefaults(pdu)
        pmod.apiPDU.setVarBinds(pdu, (((oid), pmod.Null()),))
        # Build Message
        msg = pmod.Message()
        pmod.apiMessage.setDefaults(msg)
        pmod.apiMessage.setCommunity(msg, community[1])
        pmod.apiMessage.setPDU(msg, pdu)
        return msg,pmod



    def get(self, host, oid, cb_function, default=None, **kwargs):
        if host.community_ro is None:
            cbfunction(default, host, kwargs)
            return
        msg, pmod = self._build_message(host.community_ro, oid)
        if msg is None:
            cbfunction(default, host, kwargs)
            return
        self.dispatcher.sendMessage(
                encoder.encode(msg), udp.domainName, (host.mgmt_address, 161)
                )
        self._add_request(pmod.apiPDU.getRequestID(pmod.apiMessage.getPDU(msg)), cb_function, host, default, kwargs)

