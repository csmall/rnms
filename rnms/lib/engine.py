# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
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
"""
Standard Engine class for doing those things we do over and over again in
one spot.
"""
import logging
import datetime
import zmq

from rnms.lib import zmqcore, zmqmessage
from rnms.lib.nmapclient import NmapClient
from rnms.lib.ntpclient import NTPClient
from rnms.lib.pingclient import PingClient
from rnms.lib.snmp import SNMPEngine
from rnms.lib.tcpclient import TCPClient

class RnmsEngine(object):
    """
    Base class for engines such as pollers and discovers
    use NEED_CLIENTS to enable the various clients, it is a list
    of strings:
       ntp, ping, snmp, tcp
    """
    worker_wait_seconds = 30 

    zmq_context = None
    zmq_core = None
    control_socket = None
    logger = None

    nmap_client = None
    ntp_client = None
    ping_client = None
    snmp_engine = None
    tcp_client = None

    end_thread = False

    def __init__(self, logger_name, context=None):
        self.zmq_core = zmqcore.ZmqCore()

        if context is not None:
            self.zmq_context = context
            self.control_socket = zmqmessage.control_client(self.zmq_context)
            self.zmq_core.register_zmq(self.control_socket, self.control_callback)
        else:
            self.zmq_context = zmq.Context()

        self.logger = logging.getLogger(logger_name)
        try:
            required_clients = self.NEED_CLIENTS
        except AttributeError:
            pass
        else:
            if 'nmap' in required_clients:
                self.nmap_client = NmapClient(self.logger)
            if 'ntp' in required_clients:
                self.ntp_client = NTPClient(self.zmq_core, self.logger)
            if 'ping' in required_clients:
                self.ping_client = PingClient()
            if 'snmp' in required_clients:
                self.snmp_engine = SNMPEngine(self.zmq_core, logger=self.logger)
            if 'tcp' in required_clients:
                self.tcp_client = TCPClient(self.zmq_core)
    
    def control_callback(self, socket):
        """
        Callback method for the control socket
        """
        frames = socket.recv_multipart()
        if frames[0] == zmqmessage.IPC_END:
            self.end_thread = True

    def have_working_workers(self):
        """
        Returns True if we have outstanding jobs that need stuff to do
        This is not used for pollers or collectors, only backend things
        like rrd_client
        """
        raise(NotImplemented)

    def sleep(self, wake_time):
        """
        Sleep until the specified wake_time. If the poller is escaped
        return False if we hit a break
        """
        sleep_seconds = (wake_time - datetime.datetime.now()).total_seconds()
        while self.end_thread == False and sleep_seconds > 0.0:
            #self.logger.debug('sleep secs %d',sleep_seconds)
            if not self.zmq_core.poll(sleep_seconds):
                return False
            sleep_seconds = (wake_time - datetime.datetime.now()).total_seconds()
        return self.end_thread == False
        

    def wait_for_workers(self):
        """
        This method is done after the loop to wait for the children
        to finish their work. We will wait a maximum amount of time for it
        """
        wait_seconds = self.worker_wait_seconds
        finish_wait = datetime.datetime.now() + datetime.timedelta(seconds=self.worker_wait_seconds)
        while wait_seconds > 0:
            if not self.have_working_workers():
                return
            if self.zmq_core.poll(wait_seconds) == False:
                return
            wait_seconds = (finish_wait - datetime.datetime.now()).total_seconds()
