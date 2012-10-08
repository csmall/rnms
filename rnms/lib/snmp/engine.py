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

from scheduler import SNMPScheduler
""" SNMP functions for rosenberg """

# Constants - used for oper and adminm statates
STATE_UP = 1
STATE_DOWN = 2
STATE_TESTING = 3
STATE_UNKNOWN = 4

REQUEST_GET = 0
REQUEST_GETNEXT = 1

DefaultSecurityName = 'Rosenberg'  # Arbitarily string really

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
    value_filters = {}

    def __init__(self, logger=None):
        self.value_filters = {
            'int': self.filter_int,
            'str': self.filter_str
            }
        self.dispatcher = AsynsockDispatcher()
        self.dispatcher.registerTransport(
                udp.domainName, udp.UdpSocketTransport().openClientMode()
                )
        self.dispatcher.registerRecvCbFun(self._receive_msg)
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

    def _return_value(self, value, request, error=None):
        """
        Filter the value returned by the SNMP stack and use the
        callback function.
        """
        if request['filter'] is not None:
            if request['filter'] in self.value_filters:
                value = self.value_filters[request['filter']](value)
        request['cb_func'](value, error, **(request['kwargs']))

    def socketmap(self):
        """ Returns the socket of the transportDispatcher """
        return self.dispatcher.getSocketMap()

    def poll(self):
        """
        This method should be periodically called to gather all pending
        requests and handle any responses from remote agents.

        Returns true if there is still things to do
        """
        retval = False
        self.check_timeouts()
        if self.scheduler.have_active_jobs():
            try:
                poll(0, self.dispatcher.getSocketMap())
            except socket.error:
                pass
            retval = True
        self.send_requests()
        return retval or self.scheduler.have_waiting_jobs()

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
        self.scheduler.job_received(request_id)

    def _requests_pending(self):
        return len(self.active_requests) > 0

    def _receive_msg(self, dispatcher, trans_domain, trans_address, whole_msg):
        pmod = self._pmod_from_api(api.decodeMessageVersion(whole_msg))
        if pmod is None:
            self.logger.exception("Empty pmod from receive_msg()")
            return
        while whole_msg:
            rcv_msg, whole_msg = decoder.decode(whole_msg, asn1Spec=pmod.Message())
            rcv_pdu = pmod.apiMessage.getPDU(rcv_msg)
            request_id = pmod.apiPDU.getRequestID(rcv_pdu)
            if request_id not in self.active_requests:
                self.logger.debug("receive_msg(): Cannot find request id {0}".format(request_id))
                return
            request = self.active_requests[request_id]
            # Check for error
            error_status = pmod.apiPDU.getErrorStatus(rcv_pdu)
            if error_status:
                self.logger.debug("receive_msg(): Received packet wirh errors status {0}".format(error_status.prettyPrint()))
                self._return_value(request['default'], request, error=error_status.prettyPrint())
                self._request_finished(request['id'])
            else:
                if request['type'] == REQUEST_GET:
                    self._get_response(pmod, rcv_pdu, request)
                elif request['type'] == REQUEST_GETNEXT:
                    self._getnext_response(pmod, rcv_pdu, request)
        return whole_msg

    def _get_response(self, pmod, rcv_pdu, request):
        """ Handle reception of a GET response """
        varbinds = {}
        for oid, val in pmod.apiPDU.getVarBinds(rcv_pdu):
            pretty_val = val.prettyPrint()
            if pretty_val == 'No Such Object currently exists at this OID' or pretty_val == 'No Such Instance currently exists at this OID' :
                self._return_value(request['default'], request,
                        error=pretty_val)
                self._request_finished(request['id'])
                return
            else:
                varbinds[oid.prettyPrint()] = pretty_val
        if len(varbinds) > 0:
            self._return_value(varbinds, request)
        else:
            self._return_value(request['default'], request)
        self._request_finished(request['id'])

    def _getnext_response(self, pmod, rcv_pdu, request):
        """ Handle reception of a GETNEXT response """
        if 'varbinds' not in request:
            request['varbinds'] = {}

        req_pdu = pmod.apiMessage.getPDU(request['msg'])
        var_bind_table = pmod.apiPDU.getVarBindTable(req_pdu, rcv_pdu)
        for table_row in var_bind_table:
            for oid,val in table_row:
                if request['table_oid'].isPrefixOf(oid):
                    if request['table_trim'] is None:
                        request['varbinds'][oid.prettyPrint()] = val.prettyPrint()
                    else:
                        request['varbinds'][oid[-request['table_trim']:].prettyPrint()] = val.prettyPrint()
                else:
                    self._return_value(request['varbinds'], request)
                    self._request_finished(request['id'])
                    return

        oldid = request['id']
        # Create new request
        pmod.apiPDU.setVarBinds(req_pdu, 
                map(lambda (x,y),n=pmod.Null(): ( x,n ), var_bind_table[-1]) )
        new_reqid = pmod.getNextRequestID()
        pmod.apiPDU.setRequestID(req_pdu, new_reqid)
        self.scheduler.job_update(request['id'], new_reqid)
        self.send_request(request)
        self._request_finished(oldid)


    def check_timeouts(self):
        now = time.time()
        for id,request in self.active_requests.items():
            if request['timeout'] < now:
                if request['attempt'] >= self.max_attempts:
                    self.logger.debug("Request #{0} reach maximum attempts".format(request['id']))
                    self._return_value(request['default'], request, error="Maximum poll attempts exceeded")
                    self._request_finished(request['id'])
                else:
                    self.send_request(request, False)

    def send_requests(self):
        """
        Run a loop asking the scheduler to find all requests we can kick off
        on this cycle. Returns when there is no more to send.
        """
        while True:
            request = self.scheduler.job_pop()
            if request is None:
                return
            self.send_request(request)

    def send_request(self, request, first=True):
        self.dispatcher.sendMessage(
            encoder.encode(request['msg']), udp.domainName, (request['host'].mgmt_address, 161))
        if first:
            self.scheduler.job_sent(request['id'])
            self.active_requests[request['id']] = request
            request['attempt'] = 1
        else:
            request['attempt'] += 1
        request['timeout'] = time.time() + self.default_timeout
        #self.logger.debug("send_request(): Sending request #{0} to {1} attempt {2}".format(request['id'], request['host'].mgmt_address, request['attempt']))

    def is_busy(self):
        """ Are there either jobs that are waiting or requests that are
        pending within the engine?
        """
        return self.dispatcher.jobsArePending() or self.dispatcher.transportsAreWorking()

    def _build_get_message(self, community, oid):
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

    def _build_getnext_message(self, community, oid):
        pmod = self._pmod_from_community(community)
        if pmod is None:
            self.logger.info('Could not get pmod from community %s',community)
            return None,None

        # SNMP table header
        head_vars = [ pmod.ObjectIdentifier(oid) ]

        pdu = pmod.GetNextRequestPDU()
        pmod.apiPDU.setDefaults(pdu)
        pmod.apiPDU.setVarBinds(pdu,
                map(lambda x, pmod=pmod: ( x, pmod.Null()), head_vars) )
        # Build Message
        msg = pmod.Message()
        pmod.apiMessage.setDefaults(msg)
        pmod.apiMessage.setCommunity(msg, community[1])
        pmod.apiMessage.setPDU(msg, pdu)
        return msg,pmod


    def get_int(self, host, oid, cb_function, default=None, **kwargs):
        return self.get(host, oid, cb_function, default, filt="int", **kwargs)

    def get_str(self, host, oid, cb_function, default=None, **kwargs):
        return self.get(host, oid, cb_function, default, filt="str", **kwargs)

    def get(self, host, oid, cb_function, default=None, filt=None, **kwargs):
        if host.community_ro is None:
            cb_function(default, host, kwargs)
            return
        msg, pmod = self._build_get_message(host.community_ro, oid)
        if msg is None:
            cb_function(default, host, kwargs)
            return
        self.scheduler.job_add(
                pmod.apiPDU.getRequestID(pmod.apiMessage.getPDU(msg)),
                host, cb_function, REQUEST_GET, default, filt, kwargs, msg)

    def get_table(self, host, oid, cb_function, default=None, filt=None, table_trim=None, **kwargs):
        """ Get a SNMP table from the given host and pass it to the
            cb_function
            prefix_trim: Number of numbers to return in table
        """
        if host.community_ro is None:
            cb_function(default, host, kwargs)
            return
        msg, pmod = self._build_getnext_message(host.community_ro, oid)
        if msg is None:
            cb_function(default, host, kwargs)
            return
        table_oid = pmod.ObjectIdentifier(oid) 
        self.scheduler.job_add(
                pmod.apiPDU.getRequestID(pmod.apiMessage.getPDU(msg)),
                host, cb_function, REQUEST_GETNEXT, default, filt, kwargs, msg, table_oid=table_oid, table_trim=table_trim)
                

    # Filters
    def filter_int(self, value):
        #self.logger.debug("filter_int(): Raw value is \"{0}\"".format(value))
        if value is None:
            return 0
        if type(value) is dict:
            key,value = value.popitem()
        try:
            fvalue = int(value)
        except ValueError:
            fvalue = 0
        return fvalue

    def filter_str(self, value):
        if value is None:
            return ""
        if type(value) is dict:
            key,value = value.popitem()
        try:
            fvalue = str(value)
        except ValueError:
            fvalue = ""
        return fvalue
                
    def set_default_timeout(self, timeout):
        """
        Set the default SNMP timeout for a response from agent
        """
        try:
            self.default_timeout = int(timeout)
        except ValueError:
            self.logger.warn("Bad timeout \"{0}\" given".format(timeout))


