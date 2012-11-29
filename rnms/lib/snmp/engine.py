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
import asyncore
import socket
import datetime

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
from dispatcher import SNMPDispatcher
""" SNMP functions for rosenberg """

# Constants - used for oper and adminm statates
STATE_UP = 1
STATE_DOWN = 2
STATE_TESTING = 3
STATE_UNKNOWN = 4

REQUEST_SINGLE = 0
REQUEST_TABLE = 1

REQUEST_GET = 0
REQUEST_GETNEXT = 1
REQUEST_GETBULK = 2

DefaultSecurityName = 'Rosenberg'  # Arbitarily string really

logger = logging.getLogger('snmp')

class SNMPRequest(object):
    """
    Class for filling in SNMP requests.  There may be multiple OIDs
    within the same request, for speed
    """

    replyall = False
    oid_trim = None
    req_type = REQUEST_SINGLE
    snmp_type = REQUEST_GET

    def __init__(self, host, req_type=None):
        self.host = host
        self.oids = []
        if req_type is not None:
            self.req_type = req_type
            if req_type == REQUEST_SINGLE:
                self.snmp_type = REQUEST_GET
            elif str(host.community_ro[0]) == '2':
                self.snmp_type = REQUEST_GETBULK
            else:
                self.snmp_type = REQUEST_GETNEXT

    def __repr__(self):
        return "<SNMPRequest Host:{0} #oids:{1}>".format(self.host.mgmt_address, len(self.oids))

    def add_oid(self, oid, callback, data=None, default=None, filt=None, value=None):
        """
        Add another OID to this request, there can be multiple queries to
        the same host
        """
        self.oids.append({'oid': oid, 'callback': callback, 'data': data, 'default': default, 'filter': filt, 'value': value })

    def set_replyall(self, flag):
        """
        By default, each OID will have its own callback.  Setting this 
        flag means that the first OID's callback will be used and it
        will get the whole table.
        This is similar to what happens with a get_table() except it is
        specific items
        """
        self.replyall = flag

    def send_default(self, error=None):
        """
        Fire off all the callbacks with the default value
        """
        if self.replyall:
            req = self.oids[0]
            req['callback'](req['default'], error, **(req['data']))
        else:
            for req in self.oids:
                req['callback'](req['default'], error, **(req['data']))

    def get_oid(self, oid):
        try:
            return self.oids[oid]
        except KeyError:
            return None
        return None

    def is_get(self):
        return (self.snmp_type == REQUEST_GET)

    def is_getnext(self):
        return (self.snmp_type == REQUEST_GETNEXT)

    def is_getbulk(self):
        return (self.snmp_type == REQUEST_GETBULK)

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
    address_families = [ socket.AF_INET, socket.AF_INET6 ] 

    def __init__(self, logger=None):
        self.dispatchers = { af : SNMPDispatcher(af, self.receive_msg) for af in self.address_families}
        self.value_filters = {
            'int': self.filter_int,
            'str': self.filter_str
            }
        #self.dispatcher = AsynsockDispatcher()
        #self.dispatcher.registerTransport(
        #        udp.domainName, udp.UdpSocketTransport().openClientMode()
        #        )
        #self.dispatcher.registerRecvCbFun(self._receive_msg)
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

    def _return_value(self, req_oid, value, error=None):
        """
        Filter the value returned by the SNMP stack and use the
        callback function.
        """
        if req_oid['filter'] is not None:
            try:
                value = self.value_filters[req_oid['filter']](value)
            except KeyError:
                pass
        if req_oid['data'] is None:
            req_oid['callback'](value, error)
        else:
            req_oid['callback'](value, error, **(req_oid['data']))

    def poll(self):
        """
        This method should be periodically called to gather all pending
        requests and handle any responses from remote agents.

        Returns number of jobs udner control if there is still things to do
        """
        jobcount = 0
        self.check_timeouts()
        self.send_requests()
        for dispatcher in self.dispatchers.values():
            jobcount += len(dispatcher.waiting_jobs)
        jobcount += len(self.scheduler.waiting_jobs)
        jobcount += len(self.active_requests)
        return jobcount

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

    def receive_msg(self, whole_msg, recv_addr, address_family):
        pmod = self._pmod_from_api(api.decodeMessageVersion(whole_msg))
        if pmod is None:
            self.logger.exception("Empty pmod from receive_msg()")
            return
        while whole_msg:
            rcv_msg, whole_msg = decoder.decode(whole_msg, asn1Spec=pmod.Message())
            rcv_pdu = pmod.apiMessage.getPDU(rcv_msg)

            request_id = pmod.apiPDU.getRequestID(rcv_pdu)
            self.dispatchers[address_family].del_job(request_id)
            try:
                request = self.active_requests[request_id]
            except IndexError:
                self.logger.debug("receive_msg(): Cannot find request id {0}".format(request_id))
                continue
            # Check for error
            error_status = pmod.apiPDU.getErrorStatus(rcv_pdu)
            if error_status:
                self.logger.debug("receive_msg(): Received packet with errors status {0}".format(error_status.prettyPrint()))
                request['request'].send_default()
                self._request_finished(request['id'])
            else:
                if request['request'].is_get():
                    self._get_response(pmod, rcv_pdu, request)
                elif request['request'].is_getnext():
                    if self._getnext_response(pmod, rcv_pdu, request, False) == False:
                        whole_msg = False
                elif request['request'].is_getbulk():
                    if self._getnext_response(pmod, rcv_pdu, request, True) == False:
                        whole_msg = False
        return whole_msg

    def _get_response(self, pmod, rcv_pdu, request):
        """ Handle reception of a GET response """
        reply_table = {}
        first_req_oid = None
        var_binds = pmod.apiPDU.getVarBinds(rcv_pdu)
        for idx in range(len(var_binds)):
            oid, val = var_binds[idx]
            req_oid = request['request'].oids[idx]
            if req_oid is None:
                self.logger.error('No request line for %s', oid)
                continue
            if first_req_oid is None:
                first_req_oid = req_oid
            if request['request'].oid_trim is None:
                row_oid = oid.prettyPrint()
            else:
                row_oid = oid[-request['request'].oid_trim:].prettyPrint()
            pretty_val = val.prettyPrint()
            if pretty_val == 'noSuchName' or pretty_val == 'No Such Object currently exists at this OID' or pretty_val == 'No Such Instance currently exists at this OID' :
                if request['request'].replyall:
                    reply_table[row_oid] = req_oid['default']
                else:
                    self._return_value(req_oid, req_oid['default'])
            else:
                if request['request'].replyall:
                    reply_table[row_oid] = val.prettyPrint()
                else:
                    self._return_value(req_oid, pretty_val)
        if request['request'].replyall:
            self._return_value(first_req_oid, reply_table)
        self._request_finished(request['id'])

    def _getnext_response(self, pmod, rcv_pdu, request, is_bulk):
        """ Handle reception of a GETNEXT response """
        if 'varbinds' not in request:
            request['varbinds'] = [ {} for idx  in range(len(request['request'].oids))]
        req_pdu = pmod.apiMessage.getPDU(request['msg'])
        if is_bulk:
            var_bind_table = pmod.apiBulkPDU.getVarBindTable(req_pdu, rcv_pdu)
        else:
            var_bind_table = pmod.apiPDU.getVarBindTable(req_pdu, rcv_pdu)

        for table_row in var_bind_table:
            for idx in range(len(table_row)):
                oid,val = table_row[idx]
                if request['table_oids'][idx].isPrefixOf(oid):
                    if request['request'].oid_trim is None:
                        request['varbinds'][idx][oid.prettyPrint()] = val.prettyPrint()
                    else:
                        request['varbinds'][idx][oid[-request['request'].oid_trim:].prettyPrint()] = val.prettyPrint()

        oldid = request['id']
        
        # Stop on EOM
        for idx in range(len(var_bind_table[-1])):
            oid, val = var_bind_table[-1][idx]
            if not isinstance(val, pmod.Null) and request['table_oids'][idx].isPrefixOf(oid):
                break
        else:
            if request['request'].replyall:
                request['request'].oids[0]['callback'](request['varbinds'], None, **request['request'].oids[0]['data'])
            else:
                for idx in len(request['request'].oids):
                    request['request'].oids[idx]['callback'](request['varbinds'][idx], None, **request['request'].oids[idx]['data'])
            self._request_finished(request['id'])
            return False
        # Create new request
        if request['request'].is_getbulk():
            pmod.apiBulkPDU.setVarBinds(req_pdu,
                    [ (x, pmod.null) for x,y in var_bind_table[-1]])
        else:
            pmod.apiPDU.setVarBinds(req_pdu, 
                    [ (x, pmod.null) for x,y in var_bind_table[-1] ])
        new_reqid = pmod.getNextRequestID()
        pmod.apiPDU.setRequestID(req_pdu, new_reqid)
        self.scheduler.job_update(request['id'], new_reqid)
        self.send_request(request)
        self._request_finished(oldid)
        return True


    def check_timeouts(self):
        now = time.time()
        for id,request in self.active_requests.items():
            if 'timeout' in request and request['timeout'] < now:
                if request['attempt'] >= self.max_attempts:
                    self.logger.debug("Request #{0} reach maximum attempts".format(request['id']))
                    request['request'].send_default()
                    self._request_finished(request['id'])
                else:
                    print "resending {0}".format(request)
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
        try:
            addrinfo = socket.getaddrinfo(request['host'].mgmt_address, 161)[0]
        except socket.gaierror:
            return False
        addr_family, sockaddr = addrinfo[0], addrinfo[4]
        request['sockaddr'] = sockaddr
        self.dispatchers[addr_family].send_message(request)

        #self.dispatcher.sendMessage( encoder.encode(request['msg']), udp.domainName, (request['host'].mgmt_address, 161))
        if first:
            self.scheduler.job_sent(request['id'])
            self.active_requests[request['id']] = request
            request['attempt'] = 1
        else:
            request['attempt'] += 1
        #request['timeout'] = time.time() + self.default_timeout
        #self.logger.debug("send_request(): Sending request #{0} to {1} attempt {2}".format(request['id'], request['host'].mgmt_address, request['attempt']))

    def is_busy(self):
        """ Are there either jobs that are waiting or requests that are
        pending within the engine?
        """
        return self.dispatcher.jobsArePending() or self.dispatcher.transportsAreWorking()

    def _build_get_message(self, community, request):
        pmod = self._pmod_from_community(community)
        if pmod is None:
            return None,None
        pdu = pmod.GetRequestPDU()
        pmod.apiPDU.setDefaults(pdu)
        pmod.apiPDU.setVarBinds(pdu, [(row['oid'], pmod.Null()) for row in request.oids])
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
        pmod = self._pmod_from_community(community)
        if pmod is None:
            return None,None
        pdu = pmod.SetRequestPDU()
        pmod.apiPDU.setDefaults(pdu)
        pmod.apiPDU.setVarBinds(pdu, [(row['oid'], self._set_vars(pmod,row['value'])) for row in request.oids])
        # Build Message
        msg = pmod.Message()
        pmod.apiMessage.setDefaults(msg)
        pmod.apiMessage.setCommunity(msg, community[1])
        pmod.apiMessage.setPDU(msg, pdu)
        return msg,pmod

    def _build_getnext_message(self, community, oids, is_bulk):
        pmod = self._pmod_from_community(community)
        if pmod is None:
            self.logger.info('Could not get pmod from community %s',community)
            return None,None

        # SNMP table header
        head_vars = [ pmod.ObjectIdentifier(oid) for oid in oids ]
        
        if is_bulk:
            pdu = pmod.GetBulkRequestPDU()
            pmod.apiPDU.setDefaults(pdu)
            pmod.apiBulkPDU.setNonRepeaters(pdu, 0)
            pmod.apiBulkPDU.setMaxRepetitions(pdu, 25)
            print "bulk"
        else: 
            pdu = pmod.GetNextRequestPDU()
            pmod.apiPDU.setDefaults(pdu)
            print "next"
        pmod.apiPDU.setVarBinds(pdu,
                [ (pmod.ObjectIdentifier(x), pmod.null) for x in oids])
        # Build Message
        msg = pmod.Message()
        pmod.apiMessage.setDefaults(msg)
        pmod.apiMessage.setCommunity(msg, community[1])
        pmod.apiMessage.setPDU(msg, pdu)
        return msg,pmod

    def get_int(self, host, oid, cb_func, **kw):
        """
        Function to query one SNMP item
        """
        req = SNMPRequest(host)
        req.add_oid(oid,cb_func, data=kw, filt='int')
        return self.get(req)

    def get_str(self, host, oid, cb_func, **kw):
        """
        Function to query one SNMP item
        """
        req = SNMPRequest(host)
        req.add_oid(oid,cb_func, data=kw, filt='str')
        return self.get(req)
    
    def get(self, request):
        """
        Proccess the given SNMPRequest to send out queries to a host. The
        structure may have one of more OIDs
        """
        if request.host.community_ro is None:
            request.send_default()
            return False
        msg, pmod = self._build_get_message(request.host.community_ro, request)
        if msg is None:
            request.send_default()
            return False
        self.scheduler.job_add(
                pmod.apiPDU.getRequestID(pmod.apiMessage.getPDU(msg)),
                request, msg)
        return True

    def set(self, request):
        """
        Proccess the given SNMPRequest to send out queries to a host. The
        structure may have one of more OIDs used for setting values
        """
        if request.host.community_rw is None:
            request.send_default()
            return False
        msg, pmod = self._build_set_message(request.host.community_rw, request)
        if msg is None:
            request.send_default()
            return False
        self.scheduler.job_add(
                pmod.apiPDU.getRequestID(pmod.apiMessage.getPDU(msg)),
                request, msg)
        return True

    def get_table(self, host, oids, cb_function, default=None, filt=None, table_trim=None, **kwargs):
        """ Get a SNMP table from the given host and pass it to the
            cb_function
            prefix_trim: Number of numbers to return in table
        """
        if host.community_ro is None:
            cb_function(default, host, **kwargs)
            return False
        is_getbulk = False
        if str(host.community_ro[0]) == '2':
            is_getbulk = True
        msg, pmod = self._build_getnext_message(host.community_ro, oids, is_getbulk)
        if msg is None:
            cb_function(default, host, **kwargs)
            return False
        table_oids = [ pmod.ObjectIdentifier(oid)  for oid in oids ]
        request = SNMPRequest(host, req_type=REQUEST_TABLE)
        request.oid_trim = table_trim
        request.set_replyall(True)
        for oid in oids:
            request.add_oid(oid, cb_function, data=kwargs)
        self.scheduler.job_add(
                pmod.apiPDU.getRequestID(pmod.apiMessage.getPDU(msg)),
                request, msg, table_oids=table_oids)
        return True
                

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


