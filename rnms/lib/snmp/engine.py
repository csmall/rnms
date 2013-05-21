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
import time
import socket

# import for SNMP engine
from pyasn1.codec.ber import decoder
from pysnmp.proto import api

from scheduler import SNMPScheduler
from dispatcher import SNMPDispatcher
from request import SNMPRequest, REQUEST_TABLE
""" SNMP functions for rosenberg """



DEFAULT_SECURITY_NAME = 'Rosenberg'  # Arbitarily string really


class SNMPEngine():
    """
    This class does all the heavy lifting work to produce an asynchronous
    SNMP engine.  Pollers submit their requests to it with a call back
    that gets the result.

    callback functions expect (result, host, kwargs). the kwargs are
    anything extra sent to the inital function.
    """
    active_requests = {}
    proto_mods = {}
    default_timeout = 3 # number of seconds before item is considered gone
    max_attempts = 3
    address_families = [ socket.AF_INET, socket.AF_INET6 ]
    zmq_core = None

    def __init__(self, zmq_core, logger=None):
        self.dispatchers = {
            af : SNMPDispatcher(zmq_core, af, self.receive_msg)
            for af in self.address_families}
        self.scheduler = SNMPScheduler(logger=logger)

        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger("SNMP")


    def _pmod_from_community(self, community):
        """
        Returns the Proto Module based upon the SNMP community structure
        """
        version = str(community[0])
        if version == '1':
            return api.protoModules[api.protoVersion1]
        elif version == '2':
            return api.protoModules[api.protoVersion2c]
        self.logger.info('Unknown SNMP version "%s"', version)
        return None

    def _pmod_from_api(self, api_version):
        if api_version in api.protoModules:
            return api.protoModules[api_version]
        return None

    def poll(self):
        """
        This method should be periodically called to gather all pending
        requests and handle any responses from remote agents.

        Returns number of requests udner control if there is still things to do
        """
        reqcount = 0
        self.check_timeouts()
        self.send_requests()
        for dispatcher in self.dispatchers.values():
            reqcount += len(dispatcher.waiting_requests)
        reqcount += len(self.scheduler.waiting_requests)
        reqcount += len(self.active_requests)
        return reqcount

    def _get_request(self, reqid):
        return self.active_requests.get(reqid, None)

    def _del_request(self, reqid):
        try:
            del(self.active_requests[reqid])
        except KeyError:
            pass

    def _request_finished(self, request_id):
        """ Request with given request ID is finished """
        self._del_request(request_id)
        self.scheduler.request_received(request_id)
        #self.dispatchers[address_family].del_request(request_id)

    def _requests_pending(self):
        return len(self.active_requests) > 0

    def receive_msg(self, whole_msg, recv_addr, address_family):
        pmod = self._pmod_from_api(api.decodeMessageVersion(whole_msg))
        if pmod is None:
            self.logger.exception("Empty pmod from receive_msg()")
            return
        while whole_msg:
            rcv_msg, whole_msg = decoder.decode(
                whole_msg, asn1Spec=pmod.Message())
            rcv_pdu = pmod.apiMessage.getPDU(rcv_msg)

            request_id = pmod.apiPDU.getRequestID(rcv_pdu)
            self.dispatchers[address_family].del_request(request_id)
            try:
                request = self.active_requests[request_id]
            except KeyError:
                self.logger.debug(
                    "receive_msg(): Cannot find request id %d",
                    request_id)
                continue
            # Check for error
            error_status = pmod.apiPDU.getErrorStatus(rcv_pdu)
            if error_status:
                if error_status != 2:
                    self.logger.debug(
                        "receive_msg(): Received packet with errors status %s",
                        error_status.prettyPrint())
                request.callback_default()
                self._request_finished(request.id)
            else:
                if request.is_get():
                    self._get_response(pmod, rcv_pdu, request)
                elif request.is_getnext():
                    if self._getnext_response(
                        pmod, rcv_pdu, request, False) == False:
                        whole_msg = False
                elif request.is_getbulk():
                    if self._getnext_response(
                        pmod, rcv_pdu, request, True) == False:
                        whole_msg = False
        return whole_msg

    def _get_response(self, pmod, rcv_pdu, request):
        """ Handle reception of a GET response """
        if request.varbinds is None:
            request.varbinds = {}
        first_req_oid = None
        var_binds = pmod.apiPDU.getVarBinds(rcv_pdu)
        for idx in range(len(var_binds)):
            oid, val = var_binds[idx]
            req_oid = request.oids[idx]
            if req_oid is None:
                self.logger.error('No request line for %s', oid)
                continue
            if first_req_oid is None:
                first_req_oid = req_oid
            if request.oid_trim is None:
                row_oid = oid.prettyPrint()
            else:
                row_oid = oid[-request.oid_trim:].prettyPrint()
            pretty_val = val.prettyPrint()
            if pretty_val in (
                'noSuchName',
                'No Such Object currently exists at this OID',
                'No Such Instance currently exists at this OID'
            ):
                if request.replyall:
                    request.varbinds[row_oid] = req_oid['default']
                else:
                    request.callback_single(req_oid, req_oid['default'])
            else:
                if request.replyall:
                    request.varbinds[row_oid] = val.prettyPrint()
                else:
                    request.callback_single(req_oid, pretty_val)
        if request.replyall:
            request.callback_table()
        self._request_finished(request.id)

    def _getnext_response(self, pmod, rcv_pdu, request, is_bulk):
        """ Handle reception of a GETNEXT response """
        if request.varbinds is None:
            request.varbinds = [ {} for idx  in range(len(request.oids))]
        req_pdu = pmod.apiMessage.getPDU(request.msg)
        if is_bulk:
            var_bind_table = pmod.apiBulkPDU.getVarBindTable(req_pdu, rcv_pdu)
        else:
            var_bind_table = pmod.apiPDU.getVarBindTable(req_pdu, rcv_pdu)

        for table_row in var_bind_table:
            for idx in range(len(table_row)):
                oid,val = table_row[idx]
                if request.table_oids[idx].isPrefixOf(oid):
                    if request.oid_trim is None:
                        request.varbinds[idx][oid.prettyPrint()] =\
                                val.prettyPrint()
                    else:
                        request.varbinds[idx][
                            oid[-request.oid_trim:].prettyPrint()] =\
                                val.prettyPrint()

        oldid = request.id

        # Stop on EOM
        for idx in range(len(var_bind_table[-1])):
            oid, val = var_bind_table[-1][idx]
            if not isinstance(val, pmod.Null) and \
               request.table_oids[idx].isPrefixOf(oid):
                break
        else:
            request.callback_table()
            self._request_finished(request.id)
            return False
        # Create new request
        if request.is_getbulk():
            pmod.apiBulkPDU.setVarBinds(req_pdu,
                    [ (x, pmod.null) for x,y in var_bind_table[-1]])
        else:
            pmod.apiPDU.setVarBinds(req_pdu,
                    [ (x, pmod.null) for x,y in var_bind_table[-1] ])
        new_reqid = pmod.getNextRequestID()
        pmod.apiPDU.setRequestID(req_pdu, new_reqid)
        self.scheduler.request_update(request.id, new_reqid)
        self.send_request(request)
        self._request_finished(oldid)
        return True


    def check_timeouts(self):
        now = time.time()
        for id,request in self.active_requests.items():
            if request.timeout is not None and request.timeout < now:
                if request.attempt >= self.max_attempts:
                    self.logger.debug("Request #%d reach maximum attempts",
                                      request.id)
                    request.callback_default()
                    self._request_finished(request.id)
                else:
                    #print "resending {0}".format(request.attempt)
                    self.send_request(request, False)

    def send_requests(self):
        """
        Run a loop asking the scheduler to find all requests we can kick
        off on this cycle. Returns when there is no more to send.  """
        while True:
            request = self.scheduler.request_pop()
            if request is None:
                return
            self.send_request(request)

    def send_request(self, request, first=True):
        try:
            addrinfo = socket.getaddrinfo(request.host.mgmt_address, 161)[0]
        except socket.gaierror:
            return False
        addr_family, sockaddr = addrinfo[0], addrinfo[4]
        request.sockaddr = sockaddr
        self.dispatchers[addr_family].send_message(request)

        if first:
            self.scheduler.request_sent(request.id)
            self.active_requests[request.id] = request
            request.attempt = 1
        else:
            request.attempt += 1
        request.timeout = time.time() + self.default_timeout

    def _build_get_message(self, community, request):
        pmod = self._pmod_from_community(community)
        if pmod is None:
            return None,None
        pdu = pmod.GetRequestPDU()
        pmod.apiPDU.setDefaults(pdu)
        pmod.apiPDU.setVarBinds(pdu,
                                [(row['oid'], pmod.Null())
                                 for row in request.oids])
        # Build Message
        msg = pmod.Message()
        pmod.apiMessage.setDefaults(msg)
        pmod.apiMessage.setCommunity(msg, community[1])
        pmod.apiMessage.setPDU(msg, pdu)
        return msg,pmod

    def _set_vars(self, pmod, var):
        """
        Returns the correct varbind type, used for set requests
        """
        var_type = type(var)
        if var_type == str:
            return pmod.OctectString(var)
        elif var_type == int:
            return pmod.Integer(var)
        raise ValueError('unknown type')

    def _build_set_message(self, community, request):
        """ Creat SNMP SET message for the request """
        pmod = self._pmod_from_community(community)
        if pmod is None:
            return None, None
        pdu = pmod.SetRequestPDU()
        pmod.apiPDU.setDefaults(pdu)
        pmod.apiPDU.setVarBinds(pdu,
                  [(row['oid'], self._set_vars(pmod,row['value']))
                   for row in request.oids])
        # Build Message
        msg = pmod.Message()
        pmod.apiMessage.setDefaults(msg)
        pmod.apiMessage.setCommunity(msg, community[1])
        pmod.apiMessage.setPDU(msg, pdu)
        return msg, pmod

    def _build_getnext_message(self, community, oids, is_bulk):
        """ Construct the new GETNEXT SNMP message """
        pmod = self._pmod_from_community(community)
        if pmod is None:
            self.logger.info('Could not get pmod from community %s',
                             community)
            return None, None

        # SNMP table header
        if is_bulk:
            pdu = pmod.GetBulkRequestPDU()
            pmod.apiPDU.setDefaults(pdu)
            pmod.apiBulkPDU.setNonRepeaters(pdu, 0)
            pmod.apiBulkPDU.setMaxRepetitions(pdu, 25)
        else:
            pdu = pmod.GetNextRequestPDU()
            pmod.apiPDU.setDefaults(pdu)
        pmod.apiPDU.setVarBinds(pdu,
                [ (pmod.ObjectIdentifier(x), pmod.null) for x in oids])
        # Build Message
        msg = pmod.Message()
        pmod.apiMessage.setDefaults(msg)
        pmod.apiMessage.setCommunity(msg, community[1])
        pmod.apiMessage.setPDU(msg, pdu)
        return msg, pmod

    def get_int(self, snmphost, oid, cb_func, default=None, **kw):
        """
        Function to query one SNMP item
        """
        req = SNMPRequest(snmphost)
        req.add_oid(oid, cb_func, default=default, data=kw, filt='int')
        return self.get(req)

    def get_str(self, snmphost, oid, cb_func, default=None, **kw):
        """
        Function to query one SNMP item
        """
        req = SNMPRequest(snmphost)
        req.add_oid(oid, cb_func, data=kw, default=default, filt='str')
        return self.get(req)

    def get(self, request):
        """
        Proccess the given SNMPRequest to send out queries to a host. The
        structure may have one of more OIDs
        """
        if request.host.snmp_community.readonly == '':
            request.callback_default()
            return True
        request.msg, pmod = self._build_get_message(
            request.host.snmp_community.readonly,
            request)
        if request.msg is None:
            request.callback_default()
            return False
        request.id = pmod.apiPDU.getRequestID(
            pmod.apiMessage.getPDU(request.msg))
        self.scheduler.request_add(request)
        return True

    def set(self, request):
        """
        Proccess the given SNMPRequest to send out queries to a host. The
        structure may have one of more OIDs used for setting values
        """
        if request.host.snmp_community.readwrite is None:
            request.calback_default()
            return False
        request.msg, pmod = self._build_set_message(
            request.host.snmp_community.readwrite, request)
        if request.msg is None:
            request.callback_default()
            return False
        request.id = pmod.apiPDU.getRequestID(
            pmod.apiMessage.getPDU(request.msg))
        self.scheduler.request_add(request)
        return True

    def get_table(self, snmphost, oids, cb_function, default=None,
                  table_trim=None, **kwargs):
        """
        Get a SNMP table from the given host and pass it to the
        cb_function
          prefix_trim: Number of numbers to return in table
        """
        if type(oids) == str or type(oids) == unicode:
            oids = (oids,)

        if snmphost.snmp_community.readonly == '':
            cb_function(default, snmphost, **kwargs)
            return True
        is_getbulk = False
        if snmphost.snmp_community.ro_is_snmpv2():
            is_getbulk = True
        request = SNMPRequest(snmphost, req_type=REQUEST_TABLE)
        request.msg, pmod = self._build_getnext_message(
            snmphost.snmp_community.readonly, oids, is_getbulk)
        if request.msg is None:
            cb_function(default, snmphost, **kwargs)
            return False
        request.oid_trim = table_trim
        request.table_oids = [ pmod.ObjectIdentifier(oid)  for oid in oids ]
        request.set_replyall(True)
        for oid in oids:
            request.add_oid(oid, cb_function, data=kwargs)
        request.id = pmod.apiPDU.getRequestID(
            pmod.apiMessage.getPDU(request.msg))
        self.scheduler.request_add(request)
        return True


    def set_default_timeout(self, timeout):
        """
        Set the default SNMP timeout for a response from agent
        """
        try:
            self.default_timeout = int(timeout)
        except ValueError:
            self.logger.warn("Bad timeout \"{0}\" given".format(timeout))


