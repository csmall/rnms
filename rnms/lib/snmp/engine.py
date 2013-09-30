# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012,2013 Craig Small <csmall@enc.com.au>
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
import time

from pysnmp.entity.rfc3413.oneliner import cmdgen

from scheduler import SNMPScheduler
from request import SNMPRequest
from target import get_transport_target

class SNMPEngine(object):
    zmq_core = None
    logger = None
    active_requests = {}
    default_timeout = 3 # number of seconds before item is considered gone
    max_attempts = 3

    def __init__(self, zmq_core, logger):
        self.zmq_core = zmq_core
        self.logger = logger
        self.scheduler = SNMPScheduler(logger=logger)
        self.cmd_gen = cmdgen.AsynCommandGenerator()


    def get_int(self, snmphost, oid, cb_func, default=None, **kw):
        req = SNMPRequest(snmphost, snmphost.ro_community)
        req.add_oid(oid, cb_func, default=default, data=kw, filt='int')
        return self._get(req)

    def get_str(self, snmphost, oid, cb_func, default=None, **kw):
        req = SNMPRequest(snmphost, snmphost.ro_community)
        req.add_oid(oid, cb_func, default=default, data=kw, filt='str')
        return self._get(req)

    def get_table(self, snmphost, oids, cb_func, default=None,
                  table_trim=None, **kw):
        if type(oids) in (str, unicode):
            oids = (oids,)
        req = SNMPRequest(snmphost, snmphost.ro_community)
        req.set_table()
        for oid in oids:
            req.add_oid(oid, cb_func, data=kw, default=default)
        return self._get(req)

    def _get(self, request):
        if request.community.community == '':
            request.callback_default()
            return True
        self.scheduler.request_add(request)
        return True
            

    def poll(self):
        """
        This method should be periodically called to gather all pending
        requests and handle any responses from remote agents.

        Returns number of requests udner control if there is still things to do
        """
        reqcount = 0
        # check timeouts
        try:
            if self.cmd_gen.snmpEngine.transportDispatcher.jobsArePending():
                self.cmd_gen.snmpEngine.transportDispatcher.handleTimerTick(time.time())
        except AttributeError:
            pass
        self._check_waiting_requests()
        reqcount += len(self.scheduler.waiting_requests)
        reqcount += len(self.active_requests)
        return reqcount

    def _request_finished(self, request_id):
        """ Request with given request ID is finished """
        self._del_request(request_id)
        self.scheduler.request_received(request_id)
    
    def _del_request(self, reqid):
        try:
            del(self.active_requests[reqid])
        except KeyError:
            pass
    def _check_waiting_requests(self):
        """
        Run a loop asking the scheduler to find all requests we can kick
        off on this cycle. Returns when there is no more to send.  """
        while True:
            request = self.scheduler.request_pop()
            if request is None:
                return
            self.send_request(request)

    def send_request(self, request, first=True):
        sending_oids = [cmdgen.MibVariable(x['oid']) for x in request.oids]
        if request.is_getbulk():
            request.id = self.cmd_gen.bulkCmd(
                request.community.get_auth_data(),
                get_transport_target(self.zmq_core, request.host.mgmt_address),
                0, 25,
                sending_oids,
                (self._snmp_callback, None)
            )
        elif request.is_getnext():
            request.id = self.cmd_gen.nextCmd(
                request.community.get_auth_data(),
                get_transport_target(self.zmq_core, request.host.mgmt_address),
                sending_oids,
                (self._snmp_callback, None)
            )
        else:
            request.id = self.cmd_gen.getCmd(
                request.community.get_auth_data(),
                get_transport_target(self.zmq_core, request.host.mgmt_address),
                sending_oids,
                (self._snmp_callback, None)
            )
        if first:
            self.scheduler.request_sent(request.id)
            self.active_requests[request.id] = request
            request.attempt = 1
        else:
            request.attempt += 1
        request.timeout = time.time() + self.default_timeout

    def _snmp_callback(self, request_id, errorIndication, errorStatus,
                       errorIndex, varBinds, cbCtx):
        try:
            request = self.active_requests[request_id]
        except KeyError:
            self.logger.debug(
                "receive_msg(): Cannot find request id %d",
                request_id)
        if errorIndication:
            self.logger.debug(
                'H: %d Error with SNMP: %s',
                    request.host.id, errorIndication)
            self._request_finished(request.id)
            request.callback_default(errorIndication)
            return
        if errorStatus:
            print('Errstat %s at %s' % \
                (errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex)-1] or '?')
            )
            return
    
        first_req_oid = None
        for idx,(oid,val) in enumerate(varBinds):
            try:
                req_oid = request.oids[idx]
            except IndexError:
                self.logger.error('No request oid for %s', oid.prettyPrint())
                continue
            if first_req_oid is None:
                first_req_oid = req_oid

            if request.oid_trim is None:
                row_oid = oid.prettyPrint()
            else:
                row_oid = oid[-request.oid_trim:].prettyPrint()
            row_val = val.prettyPrint()
            if request.replyall:
                request.varbinds[row_oid] = row_val
            else:
                request.callback_single(req_oid, row_val)
        if request.replyall:
            request.callback_table()
        self._request_finished(request.id)

