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
    If the with_oid option is not set to None (the default) then
    the OID is returned with that many numbers, 0 means all of the OID
    Then the inner list will be a dictionary
    """
           
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
        """ Return a single integer value """
        return self.get_one(snmphost, oid, cb_func, default=default,
                            filt='int', **kw)

    def get_str(self, snmphost, oid, cb_func, default=None, **kw):
        """ Return a single string value """
        return self.get_one(snmphost, oid, cb_func, default=default,
                            filt='str', **kw)

    def get_one(self, snmphost, oid, cb_func, default=None, filt=None, **kw):
        """ Return a single value from a single OID """
        req = SNMPRequest(snmphost, snmphost.ro_community)
        req.add_oid(oid, cb_func, default=default, data=kw, filt=filt)
        return self.get(req)

    def get_list(self, snmphost, oids, cb_func, with_oid=None, **kw):
        """ Return a list of one value per given OID """
        req = SNMPRequest(snmphost, snmphost.ro_community)
        req.with_oid = with_oid
        req.set_replyall(True)
        for oid in oids:
            req.add_oid(oid, cb_func, data=kw)
        return self.get(req)

    def get_many(self, snmphost, oids, cb_func, with_oid=None, default=None, **kw):
        """ Return a list of a list. Each primary list maps to
        one of the requested oid, which will return a list of
        values for that oid
        """
        req = SNMPRequest(snmphost, snmphost.ro_community)
        req.with_oid = with_oid
        req.set_many()
        req.set_replyall(True)
        for oid in oids:
            req.add_oid(oid, cb_func, data=kw)
        return self.get(req)

    def get_table(self, snmphost, oids, cb_func, default=None,
                  with_oid=None, **kw):
        if type(oids) in (str, unicode):
            oids = (oids,)
        req = SNMPRequest(snmphost, snmphost.ro_community)
        req.with_oid = with_oid
        req.set_table()
        for oid in oids:
            req.add_oid(oid, cb_func, data=kw, default=default)
        return self.get(req)

    def get(self, request):
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
        sending_oids = [x['rawoid'] for x in request.oids]
        if request.is_getbulk():
            request.id = self.cmd_gen.bulkCmd(
                request.community.get_auth_data(),
                get_transport_target(self.zmq_core, request.host.mgmt_address),
                0, 5,
                sending_oids,
                (self._snmp_callback, request)
            )
        elif request.is_getnext():
            request.id = self.cmd_gen.nextCmd(
                request.community.get_auth_data(),
                get_transport_target(self.zmq_core, request.host.mgmt_address),
                sending_oids,
                (self._snmp_callback, request)
            )
        else:
            request.id = self.cmd_gen.getCmd(
                request.community.get_auth_data(),
                get_transport_target(self.zmq_core, request.host.mgmt_address),
                sending_oids,
                (self._snmp_callback, request)
            )
        if first:
            self.scheduler.request_sent(request.id)
            self.active_requests[request.id] = request
            request.attempt = 1
        else:
            request.attempt += 1
        request.timeout = time.time() + self.default_timeout

    def _parse_many(self, request, var_binds):
        """ Get the raw var_binds into a list of oids which
        have a list/dict of values """
        if request.varbinds is None:
            if request.with_oid is None:
                request.varbinds = [[] for x in request.oids]
            else:
                request.varbinds = [{} for x in request.oids]
        need_more = False
        for row in var_binds:
            for idx,(oid,val) in enumerate(row):
                if request.oids[idx]['rawoid'].isPrefixOf(oid):
                    if request.with_oid is None:
                        request.varbinds[idx].append(val.prettyPrint())
                    else:
                        this_oid = oid[-request.with_oid:].prettyPrint()
                        request.varbinds[idx][this_oid] = val.prettyPrint()
        # See if we need more data
        need_more = False
        for idx,(oid,val) in enumerate(var_binds[-1]):
            if request.oids[idx]['rawoid'].isPrefixOf(oid):
                need_more = True
                break
        return need_more

    def _parse_table(self, request, var_binds):
        """ Parse the varbinds into a table which is a list of rows.
        Each row is a list or dict of values for the same entity """
        if request.varbinds is None:
            request.varbinds = []
        for row in var_binds:
            if request.with_oid is None:
                row_data = []
            else:
                row_data = {}
            for idx,(oid,val) in enumerate(row):
                if request.oids[idx]['rawoid'].isPrefixOf(oid):
                    if request.with_oid is None:
                        row_data.append(val.prettyPrint())
                    else:
                        this_oid = oid[-request.with_oid:].prettyPrint()
                        row_data[this_oid] = val.prettyPrint()
                else:
                    return False
            request.varbinds.append(row_data)
        return True

    def _parse_row(self, request, var_binds):
        first_req_oid = None
        if request.with_oid is None:
            row_vals = []
        else:
            row_vals = {}
        for idx,(oid,val) in enumerate(var_binds):
            try:
                req_oid = request.oids[idx]
            except IndexError:
                self.logger.error('No request oid for %s', oid.prettyPrint())
                continue
            if first_req_oid is None:
                first_req_oid = req_oid

            if request.with_oid is None:
                row_oid = oid.prettyPrint()
            else:
                row_oid = oid[-request.with_oid:].prettyPrint()
            row_val = val.prettyPrint()
            if request.replyall:
                if request.with_oid is None:
                    row_vals.append(row_val)
                else:
                    row_vals[row_oid] = row_val
            else:
                if request.with_oid is None:
                    request.callback_single(req_oid, row_val)
                else:
                    request.callback_single(req_oid, {row_oid: row_val})
        if request.replyall:
            request.callback_single(first_req_oid, row_vals)


    def _snmp_callback(self, request_id, errorIndication, errorStatus,
                       errorIndex, varBinds, request):
        #try:
        #    request = self.active_requests[request_id]
        #except KeyError:
        #    self.logger.debug(
        #        "receive_msg(): Cannot find request id %d",
        #        request_id)
        #    return False
        
        if errorIndication:
            self.logger.debug(
                'H: %d Error with SNMP: %s',
                    request.host.id, errorIndication)
            self._request_finished(request.id)
            request.callback_default(errorIndication)
            return False
        if errorStatus:
            print('Errstat %s at %s' % \
                (errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex)-1] or '?')
            )
            return False
        if request.is_many():
            if self._parse_many(request, varBinds) == True:
                return True

        elif request.is_table():
            if self._parse_table(request, varBinds) == True:
                return True
        else:
            self._parse_row(request, varBinds)
        if request.is_table() or request.is_many():
            request.callback_table()
        self._request_finished(request.id)
        return False

