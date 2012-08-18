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

DefaultSecurityName = 'Rosenberg'  # Arbitarily string really

class SNMPEngine():
    """ 
    This class does all the heavy lifting work to produce an asynchronous
    SNMP engine.  Pollers submit their requests to it with a call back
    that gets the result.

    callback functions expect (result, host, kwargs). the kwargs are
    anything extra sent to the inital function.
    """
    polling_jobs = {}
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

    def _return_value(self, value, job, error=None):
        """
        Filter the value returned by the SNMP stack and use the
        callback function.
        """
        if job['filter'] is not None:
            if job['filter'] in self.value_filters:
                value = self.value_filters[job['filter']](value)
        job['cb_func'](value, job['host'], job['kwargs'], error=error)

    def socketmap(self):
        """ Returns the socket of the transportDispatcher """
        return self.dispatcher.getSocketMap()

    def poll(self):
        """
        Run through all the jobs and check timeout of all pending
        requests. Returns true if there is still things to do
        """
        poll(0.2, self.dispatcher.getSocketMap())
        self.send_jobs()
        self.check_timeouts()
        return self.scheduler.have_jobs() or self.dispatcher.jobsArePending() or self.dispatcher.transportsAreWorking()

    def _get_job(self, reqid):
        return self.polling_jobs.get(reqid, None)

    def _del_request(self, reqid):
        try:
            del(self.polling_jobs[reqid])
        except KeyError:
            pass

    def _requests_pending(self):
        return len(self.polling_jobs) > 0

    def _receive_msg(self, dispatcher, trans_domain, trans_address, msg):
        pmod = self._pmod_from_api(api.decodeMessageVersion(msg))
        if pmod is None:
            self.logger.exception("Empty pmod from receive_msg()")
            return
        while msg:
            rcv_msg, msg = decoder.decode(msg, asn1Spec=pmod.Message())
        rcv_pdu = pmod.apiMessage.getPDU(rcv_msg)
        request_id = pmod.apiPDU.getRequestID(rcv_pdu)
        if request_id not in self.polling_jobs:
            self.logger.debug("receive_msg(): Cannot find request id {0}".format(request_id))
            return
        request = self.polling_jobs[request_id]
        # Check for error
        error_status = pmod.apiPDU.getErrorStatus(rcv_pdu)
        if error_status:
            self.logger.debug(error_status.prettyPrint())
            self._return_value(request['default'], request, error=error_status.prettyPrint())
        else:
            varbinds = {}
            for oid, val in pmod.apiPDU.getVarBinds(rcv_pdu):
                varbinds[oid.prettyPrint()] = val.prettyPrint()
            if len(varbinds) > 0:
                self._return_value(varbinds, request)
            else:
                self._return_value(request['default'], request)
        self._del_request(request_id)
        self.scheduler.job_received(request_id)

    def check_timeouts(self):
        now = time.time()
        for id,job in self.polling_jobs.items():
            if job['timeout'] < now:
                if job['attempt'] >= self.max_attempts:
                    self.logger.debug("Job {0} reach maximum attempts".format(job['reqid']))
                    self._return_value(job['default'], job, error="Maximum poll attempts exceeded")
                    self._del_request(job['reqid'])
                    self.scheduler.job_received(job['reqid'])
                else:
                    self.send_job(job, False)

    def send_jobs(self):
        """
        Run a loop asking the scheduler to find all jobs we can kick off
        on this cycle. Returns when there is no more to send.
        """
        while True:
            job = self.scheduler.job_pop()
            if job is None:
                return
            self.send_job(job)

    def send_job(self, job, first=True):
        self.dispatcher.sendMessage(
            encoder.encode(job['msg']), udp.domainName, (job['host'].mgmt_address, 161))
        if first:
            self.scheduler.job_sent(job['reqid'])
            self.polling_jobs[job['reqid']] = job
            job['attempt'] = 1
        else:
            job['attempt'] += 1
        job['timeout'] = time.time() + self.default_timeout
        self.logger.debug("send_job(): Sending job {0} to {1} attempt {2}".format(job['reqid'], job['host'].mgmt_address, job['attempt']))

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


    def get_int(self, host, oid, cb_function, default=None, **kwargs):
        return self.get(host, oid, cb_function, default, filt="int", **kwargs)

    def get_str(self, host, oid, cb_function, default=None, **kwargs):
        return self.get(host, oid, cb_function, default, filt="str", **kwargs)

    def get(self, host, oid, cb_function, default=None, filt=None, **kwargs):
        if host.community_ro is None:
            cbfunction(default, host, kwargs)
            return
        msg, pmod = self._build_message(host.community_ro, oid)
        if msg is None:
            cbfunction(default, host, kwargs)
            return
        self.scheduler.job_add(
                pmod.apiPDU.getRequestID(pmod.apiMessage.getPDU(msg)),
                host, cb_function, default, filt, kwargs, msg)


    # Filters
    def filter_int(self, value):
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
                


