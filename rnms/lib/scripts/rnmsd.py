# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2013-2015 Craig Small <csmall@enc.com.au>
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
Module for the master daemon that runs all the sub-processes for
RoseNMS
Daemonizing code comes from
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
"""
import logging
import threading
import sys

import zmq

from tg import config

from rnms.lib.cmdline import RnmsCommand
from rnms.lib.poller import Poller
from rnms.lib.consolidate import Consolidator
from rnms.lib.sla_analyzer import SLAanalyzer
from rnms.lib.att_discover import AttDiscover
from rnms.lib.snmptrapd import SNMPtrapd
from rnms.lib import zmqmessage


class Rnmsd(RnmsCommand):
    """
    Master object for the RoseNMS daemon. This daemon is responsible
    for starting other sub-threads either continuously or at particular times.
    """
    enable_poller = True
    enable_consolidator = True
    args = None
    threads = None
    __set_pidfile__ = False

    def __init__(self, name):
        super(Rnmsd, self).__init__(name)
        self.zmq_context = zmq.Context()
        self.zmq_poller = zmq.Poller()
        self.control_socket = zmqmessage.control_server(self.zmq_context)
        self.threads = {}
        self.end_threads = False
        self.timeout = 10

    def real_command(self):
        """ The entry point for the RNMS daemon """
        self.logger = logging.getLogger('rnms')

        if not self.options.log_debug and not self.options.no_daemon:
            self.daemonize()
        self.create_pidfile()

        self._create_info_socket()

        self.poller = Poller(zmq_context=self.zmq_context, do_once=False)
        self.threads['poller'] = threading.Thread(target=self.poller.main_loop)
        self.threads['poller'].start()

        self.consolidator = Consolidator(zmq_context=self.zmq_context,
                                         do_once=False)
        self.threads['consolidator'] = threading.Thread(
            target=self.consolidator.consolidate, name='consolidator')
        self.threads['consolidator'].start()

        self.sla_analyzer = SLAanalyzer(zmq_context=self.zmq_context,
                                        do_once=False)
        self.threads['sla_analyzer'] = threading.Thread(
            target=self.sla_analyzer.analyze, name='sla_analyzer')
        self.threads['sla_analyzer'].start()

        self.att_discover = AttDiscover(zmq_context=self.zmq_context,
                                        do_once=False)
        #self.threads['att_discover'] = threading.Thread(
        #target=self.att_discover.discover, name='att_discover')
        #self.threads['att_discover'].start()

        # main loop
        self.snmptrapd = SNMPtrapd(zmq_context=self.zmq_context)
        self.threads['snmptrapd'] = threading.Thread(target=self.snmptrapd.run)
        self.threads['snmptrapd'].start()
        while True:
            try:
                if not self._poll():
                    return -1
                ret_val = self._check_threads()
                if ret_val is not None:
                    return ret_val
            except KeyboardInterrupt:
                self.logger.debug('User Interrupt Pressed, shutting down')
                self._shutdown()

    def _shutdown(self):
        """ Method that is called to shutdown the daemon """
        self.control_socket.send(zmqmessage.IPC_END)
        self.end_threads = True
        self.timeout = 1

    def _poll(self):
        """ Poll the ZMQ socket and handle any requests """
        try:
            events = dict(self.zmq_poller.poll(self.timeout*1000))
        except zmq.error.ZMQError as err:
            self.logger.info("ZMQ Error: {}\n".format(
                err.message))
            return True
        for sock, event in events.items():
            if sock == self.info_socket:
                self.handle_info_read()
                continue
            # Unhandled socket?!
            self.logger.critical('Unhandled event from zmq poller')
            self._shutdown()
            return False
        return True

    def _check_threads(self):
        """ Check the status of all sub-threads. Return None if
        all is good, otherwise the return value """
        waiting_threads = []
        for tname, tobj in self.threads.items():
            if tobj.is_alive():
                if self.end_threads:
                    waiting_threads.append(tname)
            elif not self.end_threads:
                self.logger.critical('Thread %s has died.', tname)
                self._shutdown()
                return -1
        if self.end_threads:
            if waiting_threads == []:
                self.logger.debug('All threads finished, exiting')
                return 0
            else:
                self.logger.debug('Waiting for threads {}'.
                                  format(', '.join(waiting_threads)))
        return None

    def handle_info_read(self):
        frames = self.info_socket.recv_multipart()
        if frames[0] == zmqmessage.IPC_INFO_REQ:
            self.info_socket.send(zmqmessage.IPC_INFO_REP, zmq.SNDMORE)
            self.info_socket.send_json(
                {'tasks': [tname for tname in self.threads.keys()]})
        else:
            self.error('Info socket received invalid command')

    def _create_info_socket(self):
        try:
            port_num = int(config['info_port'])
        except (KeyError, ValueError):
            self.logger.critical("Configuration doesn't have key 'info_port'")
            sys.exit(1)
        self.info_socket = self.zmq_context.socket(zmq.REP)
        self.info_socket.bind('tcp://127.0.0.1:{}'.format(port_num))
        self.zmq_poller.register(self.info_socket, zmq.POLLIN)


def main():
    rnmsd = Rnmsd(__name__)
    return rnmsd.run()

if __name__ == '__main__':
    sys.exit(main())
