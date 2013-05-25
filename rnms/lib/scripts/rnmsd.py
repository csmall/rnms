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
Module for the master daemon that runs all the sub-processes for 
Rosenberg
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
    Master object for the Rosenberg NMS daemon. This daemon is responsible
    for starting other sub-threads either continuously or at particular times.
    """
    enable_poller = True
    enable_consolidator = True
    args = None
    threads = None

    def __init__(self, name):
        super(Rnmsd, self).__init__(name)
        self.zmq_context = zmq.Context()
        self.zmq_poller = zmq.Poller()
        self.control_socket = zmqmessage.control_server(self.zmq_context)
        self.threads = {}

    def real_command(self):
        """ The entry point for the RNMS daemon """
        self.logger = logging.getLogger('rnms')
        self._create_info_socket()

        self.poller = Poller(zmq_context=self.zmq_context, do_once=False)
        self.threads['poller'] = threading.Thread(target=self.poller.main_loop)
        self.threads['poller'].start()

        self.consolidator = Consolidator(zmq_context=self.zmq_context, do_once=False)
        self.threads['consolidator'] = threading.Thread(target=self.consolidator.consolidate, name='consolidator')
        self.threads['consolidator'].start()

        self.sla_analyzer = SLAanalyzer(zmq_context=self.zmq_context, do_once=False)
#        self.threads['sla_analyzer'] = threading.Thread(target=self.sla_analyzer.analyze, name='sla_analyzer')
#        self.threads['sla_analyzer'].start()

        self.att_discover = AttDiscover(zmq_context=self.zmq_context, do_once=False)
        #self.threads['att_discover'] = threading.Thread(target=self.att_discover.discover, name='att_discover')
        #self.threads['att_discover'].start()

        # main loop
        self.snmptrapd = SNMPtrapd(zmq_context=self.zmq_context)
        self.threads['snmptrapd'] = threading.Thread(target=self.snmptrapd.run)
        self.threads['snmptrapd'].start()
        while True:
            try:
                events = dict(self.zmq_poller.poll(10000))
                for sock,event in events.items():
                    if sock == self.info_socket:
                        self.handle_info_read()
                        continue
                    # Unhandled socket?!
                    self.logger.critical('Unhandled event from zmq poller')
                    self._shutdown()
                    return -1

                for tname, tobj in self.threads.items():
                    if not tobj.is_alive():
                        self.logger.critical('Thread %s has died.', tname)
                        self._shutdown()
                        return -1
            except KeyboardInterrupt:
                self._shutdown()
                return 0

    def _shutdown(self):
        """ Method that is called to shutdown the daemon """
        self.control_socket.send(zmqmessage.IPC_END)

    def handle_info_read(self):
        frames = self.info_socket.recv_multipart()
        if frames[0] == zmqmessage.IPC_INFO_REQ:
            self.info_socket.send(zmqmessage.IPC_INFO_REP, zmq.SNDMORE)
            self.info_socket.send_json({'tasks':[tname for tname in
                                                self.threads.keys()]})
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
