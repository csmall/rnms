# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013-2014 Craig Small <csmall@enc.com.au>
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
import socket
import time
import sys

import transaction

from pyasn1.codec.ber import decoder
from pyasn1.type import univ as pyasn_types
from pysnmp.proto import api

from rnms.lib import zmqcore
from rnms.lib.engine import RnmsEngine
from rnms.lib.gettid import gettid
from rnms.model import DBSession, Host, SnmpTrap

SNMP_TRAP_OID = \
    pyasn_types.ObjectIdentifier().prettyIn('1.3.6.1.6.3.1.1.4.1.0')

CACHE_SECONDS = 60
TRAP_DUPLICATE_SECONDS = 5


class SNMPtrap_dispatcher(zmqcore.Dispatcher):
    cb_fun = None

    def __init__(self, zmq_core, address_family, host, port, cb_fun):
        super(SNMPtrap_dispatcher, self).__init__(zmq_core)
        self.create_socket(address_family, socket.SOCK_DGRAM)
        try:
            self.bind(('', port))
        except socket.error as errmsg:
            print 'Cannot bind to socket {}: {}'.format(
                port, errmsg)
            sys.exit(1)
        #self.listen(5)
        self.cb_fun = cb_fun

    def handle_read(self):
        try:
            recv_msg, recv_addr = self.recvfrom(65535)
            if not recv_msg:
                self.handle_close()
                return
            else:
                self.cb_fun(recv_addr, recv_msg)
                return
        except socket.error:
            print('handle_read: socket error')

    def writable(self):
        return False


class SNMPtrapd(RnmsEngine):
    zmq_core = None
    address_families = (socket.AF_INET6, )
    host_cache = None
    trap_cache = None

    def __init__(self, zmq_context=None, bind_port=6162):
        super(SNMPtrapd, self).__init__('trapd', zmq_context)
        self.dispatcher = SNMPtrap_dispatcher(self.zmq_core, socket.AF_INET6,
                                              '', bind_port, self.recv_trap)
        self.host_cache = {}
        self.trap_cache = {}

    def load_config(self):
        """ Load the configuration from the Database """

    def run(self):
        self.logger.info('SNMP trap daemon started TID:%s', gettid())
        cache_clean_time = time.time() + CACHE_SECONDS
        while True:
            now = time.time()
            if now > cache_clean_time:
                self.clean_host_cache()
                cache_clean_time = now + CACHE_SECONDS
            sleep_time = max(cache_clean_time - now, 0)
            if not self.zmq_core.poll(sleep_time):
                return
            if self.end_thread:
                return

    def recv_trap(self, recv_addr, recv_msg):
        # Fix the IPv4 mapped addresses
        if recv_addr[0][:7] == '::ffff:':
            host_ip = recv_addr[0][7:]
        else:
            host_ip = recv_addr[0]
        host_id = self._get_host_id(host_ip)
        if host_id is None:
            self.logger.debug(
                'Notification message from unknown host %s', host_ip)
            return
        while recv_msg:
            msg_ver = int(api.decodeMessageVersion(recv_msg))
            if msg_ver in api.protoModules:
                pmod = api.protoModules[msg_ver]
            else:
                self.logger.info(
                    'H:%d - Unsupported SNMP version %s from %s',
                    host_id, msg_ver, host_ip)
                return

            req_msg, recv_msg = decoder.decode(
                recv_msg, asn1Spec=pmod.Message(),)

            req_pdu = pmod.apiMessage.getPDU(req_msg)
            if req_pdu.isSameTypeWith(pmod.TrapPDU()):
                trap_oid = None

                if msg_ver == api.protoVersion1:
                    trap_oid = self._get_trapv1_oid(pmod, req_pdu)
                    if trap_oid is None:
                        return
                    new_trap = SnmpTrap(host_id, trap_oid)
                    new_trap.set_uptime(
                        pmod.apiTrapPDU.getTimeStamp(req_pdu).prettyPrint())
                    var_binds = pmod.apiTrapPDU.getVarBindList(req_pdu)
                else:
                    new_trap = SnmpTrap(host_id, None)
                    var_binds = pmod.apiPDU.getVarBindList(req_pdu)

                for var_bind in var_binds:
                    oid, val = pmod.apiVarBind.getOIDVal(var_bind)
                    if oid == SNMP_TRAP_OID:
                        new_trap.trap_oid = val.prettyPrint()
                    else:
                        new_trap.set_varbind(oid.prettyPrint(),
                                             val.prettyPrint())
                if new_trap.trap_oid is None:
                    self.logger.info('H:%d Trap with no trap_oid?')
                else:
                    if self._duplicate_trap(host_id, new_trap.trap_oid):
                        self.logger.debug(
                            'H:%d Duplicate Trap,not added OID:%s',
                            host_id, new_trap.trap_oid)
                    else:
                        self.logger.debug(
                            'H:%d New Trap v%s OID:%s',
                            host_id, msg_ver, new_trap.trap_oid)
                        DBSession.add(new_trap)
                        transaction.commit()

    def clean_host_cache(self):
        clean_time = time.time() - CACHE_SECONDS
        for key, cache in self.host_cache.items():
            if cache[1] < clean_time:
                self.logger.debug('H:%d Deleting host from cache.', key)
                del (self.host_cache[key])

        clean_time = time.time() - TRAP_DUPLICATE_SECONDS
        for key, last_seen in self.trap_cache.items():
            if last_seen < clean_time:
                del (self.trap_cache[key])

    def _get_host_id(self, address):
        """ Get the host_id for the given address. It may be cached
        for efficiency """
        try:
            return self.host_cache[address][0]
        except KeyError:
            pass
        now = time.time()
        host = Host.by_address(address)
        if host is None:
            self.host_cache[address] = (None, now)
        else:
            self.host_cache[address] = (host.id, now)
        return self.host_cache[address][0]

    def _duplicate_trap(self, host_id, trap_oid):
        """ Is this a duplicate trap?
        Have we seen the same OID from the same host within
        TRAP_DUPLICATE_SECONDS
        """
        now = time.time()
        key = '{}:{}'.format(host_id, trap_oid)
        try:
            trap_time = self.trap_cache[key]
        except KeyError:
            self.trap_cache[key] = now
            return False
        if trap_time < now - TRAP_DUPLICATE_SECONDS:
            trap_time = now
            return False
        trap_time = now
        return True

    @classmethod
    def _get_trapv1_oid(self, pmod, req_pdu):
        """
        Convert SNMP v1 Trap details into a SNMP v2 Trap OID.
        This is specified in RFC 1907
        """
        generic_trap = pmod.apiTrapPDU.getGenericTrap(req_pdu)
        if generic_trap == 6:
            # Enterprise trap <enterprise>.<specific>
            return '{}.{}'.format(
                pmod.apiTrapPDU.getEnterprise(req_pdu).prettyPrint(),
                pmod.apiTrapPDU.getSpecificTrap(req_pdu)
                )
        try:
            generic_trap_int = int(generic_trap) + 1
        except ValueError:
            return None
        else:
            return '1.3.6.1.6.3.1.1.5.{}'.format(generic_trap_int)
