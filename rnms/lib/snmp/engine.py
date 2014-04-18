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

from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.entity import engine
from pysnmp.proto.rfc1905 import NoSuchObject, NoSuchInstance
from pysnmp.error import PySnmpError

from scheduler import SNMPScheduler
from request import SNMPRequest, SNMPGetTableRequest, SNMPGetRequest,\
    SNMPGetListRequest


class SNMPEngine(object):
    """
    Main object for SNMP querying, both get and set. There are several
    different methods for this object:

        get_one(): Requires a single OID and returns a single value or
          { oid: value } with oid
        get_list(): Requires a list of OIDs and returns a list of values,
           one per OID or a dictionary of oid/values
        get_table(): Requires a list of OIDs and returns a list of a list
           columns are each oid, the row is each entry for that column
           [[oid1val1, oid2val1, oid3val1],[oid1val2, oid2val2, oid3val3]]
           Used for returning all from same SNMP table
        get_many(): Requires a list of OIDs and returns a list of lists,
           row is each oid, which is a list of returned values
           Used for different tables
    The with_oid option is None by default, meaning no OID is returned
    with the values. When this option is set, instead of just the values
    a (oid, value) tuple is returned. The option is a number of digits
    to return, with 0 meaning the entire OID
    """

    zmq_core = None
    logger = None
    active_requests = {}
    default_timeout = 3  # number of seconds before item is considered gone
    max_attempts = 3

    def __init__(self, zmq_core, logger):
        self.zmq_core = zmq_core
        self.logger = logger
        self.scheduler = SNMPScheduler(logger=logger)

        self.transport_dispatcher = AsynsockDispatcher()
        self.transport_dispatcher.setSocketMap(zmq_core.socket_map)
        snmp_engine = engine.SnmpEngine()
        snmp_engine.registerTransportDispatcher(self.transport_dispatcher)
        self.cmd_gen = cmdgen.AsynCommandGenerator(snmpEngine=snmp_engine)

    def get_int(self, snmphost, oid, cb_func, **kw):
        """ Return a single integer value """
        return self.get_one(snmphost, oid, cb_func,
                            filter='int', **kw)

    def get_str(self, snmphost, oid, cb_func, **kw):
        """ Return a single string value """
        return self.get_one(snmphost, oid, cb_func,
                            filter='str', **kw)

    def get_one(self, snmphost, oid, cb_func, with_oid=None, **kw):
        """ Return a single value from a single OID """
        req = SNMPGetRequest(snmphost, snmphost.ro_community)
        req.with_oid = with_oid
        req.add_oid(oid, callback=cb_func, **kw)
        return self.get(req)

    def get_list(self, snmphost, oids, cb_func, with_oid=None, **kw):
        """ Return a list of one value per given OID """
        req = SNMPGetListRequest(snmphost, snmphost.ro_community,
                                 cb_func, **kw)
        req.with_oid = with_oid
        for oid in oids:
            req.add_oid(oid)
        return self.get(req)

    def get_many(self, snmphost, oids, cb_func, with_oid=None, **kw):
        """ Return a list of a list. Each primary list maps to
        one of the requested oid, which will return a list of
        values for that oid
        """
        req = SNMPRequest(snmphost, snmphost.ro_community)
        req.with_oid = with_oid
        req.set_many()
        req.set_replyall(True)
        for oid in oids:
            req.add_oid(oid, cb_func, **kw)
        return self.get(req)

    def get_table(self, snmphost, oids, cb_func, with_oid=None, **kw):
        if type(oids) in (str, unicode):
            oids = (oids,)
        req = SNMPGetTableRequest(snmphost, snmphost.ro_community,
                                  cb_func, **kw)
        req.with_oid = with_oid
        for oid in oids:
            req.add_oid(oid)
        return self.get(req)

    def get(self, request):
        if request.community.community == '':
            request.callback_none()
            return True
        self.scheduler.request_add(request)
        return True

    def set(self, request):
        if request.community.community == '':
            request.callback_none()
            return True
        self.scheduler.request_add(request)

    def poll(self):
        """
        This method should be periodically called to gather all pending
        requests and handle any responses from remote agents.

        Returns number of requests udner control if there is still things to do
        """
        reqcount = 0
        # check timeouts
        try:
            if self.transport_dispatcher.jobsArePending():
                self.transport_dispatcher.handleTimerTick(time.time())
        except AttributeError:
            pass
        except PySnmpError as errmsg:
            self.logger.error('Problem with SNMP: %s', errmsg)
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
        request.prepare(self.cmd_gen, self._snmp_callback)
        if first:
            self.scheduler.request_sent(request.id)
            self.active_requests[request.id] = request
            request.attempt = 1
        else:
            request.attempt += 1
        request.timeout = time.time() + self.default_timeout

    @classmethod
    def _format_value(cls, request, oid, raw_value):
        """ Parse the SNMP returned value """
        if isinstance(raw_value, (NoSuchInstance, NoSuchObject)):
            val = None
        else:
            val = raw_value.prettyPrint()
        if request.with_oid is None:
            return val
        else:
            return (oid[-request.with_oid:].prettyPrint(), val)

    def _parse_many(self, request, var_binds):
        """ Get the raw var_binds into a list of oids which
        have a list/dict of values """
        if request.varbinds is None:
            request.varbinds = [[] for x in request.oids]
        need_more = False
        for row in var_binds:
            for idx, (oid, val) in enumerate(row):
                if request.oids[idx].is_prefix_of(oid):
                    request.varbinds[idx].append(
                        self._format_value(request, oid, val))
        # See if we need more data
        need_more = False
        for idx, (oid, val) in enumerate(var_binds[-1]):
            if request.oids[idx].is_prefix_of(oid):
                need_more = True
                break
        return need_more

    def _parse_table(self, request, var_binds):
        """ Parse the varbinds into a table which is a list of rows.
        Each row is a list or dict of values for the same entity """
        if request.varbinds is None:
            request.varbinds = []
        for row in var_binds:
            row_data = []
            for idx, (oid, val) in enumerate(row):
                if request.oids[idx].is_prefix_of(oid):
                    row_data.append(self._format_value(request, oid, val))
                else:
                    return False
            request.varbinds.append(row_data)
        return True

    def _parse_row(self, request, var_binds):
        first_req_oid = None
        row_vals = []
        for idx, (oid, val) in enumerate(var_binds):
            try:
                req_oid = request.oids[idx]
            except IndexError:
                self.logger.error('No request oid for %s', oid.prettyPrint())
                continue
            if first_req_oid is None:
                first_req_oid = req_oid

            if request.is_replyall():
                row_vals.append(self._format_value(request, oid, val))
            else:
                request.callback_single(req_oid,
                                        self._format_value(request, oid, val))
        if request.is_replyall():
            request.varbinds = row_vals
            request.callback_table()

    def _snmp_callback(self, request_id, error_indication, error_status,
                       error_index, var_binds, request):

        if error_indication:
            self.logger.debug(
                'H: %d Error with SNMP: %s',
                request.host.id, error_indication)
            self._request_finished(request.id)
            request.callback_none(error_indication)
            return False
        if error_status:
            self.logger.debug(
                'H:%d SNMP Errstat %s at %s',
                request.host.id, error_status.prettyPrint(),
                error_index and var_binds[int(error_index)-1] or '?')
            self._request_finished(request.id)
            request.callback_none(error_status)
            return False
        if request.is_many():
            if self._parse_many(request, var_binds):
                return True

        elif request.is_table():
            if self._parse_table(request, var_binds):
                return True
        else:
            self._parse_row(request, var_binds)
        if request.is_table() or request.is_many():
            request.callback_table()
        self._request_finished(request.id)
        return False
