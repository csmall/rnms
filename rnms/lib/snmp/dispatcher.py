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
from pyasn1.codec.ber import encoder, decoder

logger = logging.getLogger('snmp')

class SNMPDispatcher(asyncore.dispatcher):

    timeout = 3
    max_attempts = 3

    def __init__(self, address_family, recv_cb):
        asyncore.dispatcher.__init__(self)
        self.create_socket(address_family, socket.SOCK_DGRAM)
        self.waiting_jobs = []
        self.sent_jobs = {}
        self.recv_cb = recv_cb
        self.address_family = address_family

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        recv_msg, recv_addr = self.recvfrom(8192)
        self.recv_cb(recv_msg, recv_addr, self.address_family)

    def writable(self):
        return self.have_waiting_jobs()

    def handle_write(self):
        try:
            new_job = self.waiting_jobs.pop()
        except IndexError:
            return
        new_job['timeout'] = time.time() + self.timeout
        try:
            self.sendto(encoder.encode(new_job['msg']), new_job['sockaddr'])
        except socket.error as errmsg:
            logger.error("Socket error for sendto %s", new_job['sockaddr'])
        self.sent_jobs[new_job['id']] = new_job

    def send_message(self, request):
        self.waiting_jobs.append(request)

    def del_job(self, job_id):
        del(self.sent_jobs[job_id])

    def have_waiting_jobs(self):
        return (self.waiting_jobs != [])

