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

class SnmpEngine():
    """ 
    This class does all the heavy lifting work to produce an asynchronous
    SNMP engine.  Pollers submit their requests to it with a call back
    that gets the result.

    callback functions expect (result, host, kwargs). the kwargs are
    anything extra sent to the inital function.
    """
    polling_jobs = {}
    waiting_jobs = {}
    proto_mods = {}
    default_timeout = 3 # number of seconds before item is considered gone

    def __init__(self):
        self.dispatcher = AsynsockDispatcher()
        self.dispatcher.registerTransport(
                udp.domainName, udp.UdpSocketTransport().openClientMode()
                )
        self.dispatcher.registerRecvCbFun(self._receive_msg)
        self.scheduler = SNMPScheduler()

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
        Run through all the jobs and check timeout of all pending
        requests. Returns true if there is still things to do
        """
        poll(0.2, self.dispatcher.getSocketMap())
        return self.scheduler.have_jobs() or self.dispatcher.jobsArePending() or self.dispatcher.transportsAreWorking()

    def _queue_job(self, reqid, cb_func, host, default ,kwargs):
        self.waiting_jobs[reqid] = {
                'cb_func': cb_func,
                'host': host,
                'default': default,
                'kwargs': kwargs }

    def _get_job(self, reqid):
        return self.polling_jobs.get(reqid, None)

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

    def send_messages(self):
        job = self.scheduler.job_pop()
        if job is None:
            return
        self.dispatcher.sendMessage(
                encoder.encode(job['msg']), udp.domainName, (job['host'].mgmt_address, 161)
                )

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
        self.scheduler.job_add(
                pmod.apiPDU.getRequestID(pmod.apiMessage.getPDU(msg)),
                host, cb_function, default, kwargs, msg)



class SNMPScheduler():
    """
    The SNMP Scheuduler is given a series of SNMP polling jobs and stores 
    them.  When the poller needs more items to poll, the scheduler determines
    the best items to use, dependent on what is currently been polling.
    """
    waiting_jobs = []
    active_jobs = {}

    active_addresses = {}

    def job_add(self, reqid, host, cb_func, default, kwargs, msg):
        """
        Adds a new job to the waiting queue
        """
        self.waiting_jobs.insert(0, {
            'reqid': reqid,
            'host': host,
            'cb_func': cb_func,
            'default': default,
            'kwargs': kwargs,
            'msg': msg
            })

    def job_del(self, reqid):
        """
        Remove a pending job based upon its request ID
        """
        pass # waitingor no:w


    def job_pop(self):
        """
        Returns the "best" job to be polled next, depending what the
        scheduler decides is "best". Returns None if there are no best
        items.

        Callers should deal with each job first, for example calling
        job_sent() before calling this method again.
        """
        for job in self.waiting_jobs:
            if job.host.mgmt_address not in self.active_addresses:
                return job
        return None


    def job_sent(self, reqid):
        """
        The Engine needs to tell the Scheduler that the job has been
        sent. This will put this job into the active list and out
        of pending list.
        """
        for i,job in enumerate(self.waiting_jobs):
            if job.reqid == reqid:
                mgmt_address = job.host.mgmt_address
                if mgmt_address in self.active_addresses:
                    self.active_addresses[mgmt_address] += 1
                else:
                    self.active_addresses[mgmt_address] = 1
                self.active_jobs[reqid] = job
                del(self.waiting_jobs[i])
                return

    def job_received(self, reqid):
        """
        The Engine calls this when either there has been a reply OR
        the Engine has given up on trying to poll this item.  In any
        case it frees up the polling of the remote device.
        """
        if reqid in self.active_jobs:
            job = self.active_jobs[reqid]
            mgmt_address = job.host.mgmt_address
            if mgmt_address in self.active_addresses:
                if self.active_addresses[mgmt_address] == 1:
                    self.active_addrrsses[mgmt_address] += 1
                else:
                    self.active_addrrsses[mgmt_address] = 1
            del(self.active_jobs[reqid])

    def have_jobs(self):
        return len(self.active_jobs) > 0 or len(self.waiting_jobs) > 0
