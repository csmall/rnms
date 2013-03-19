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
import os
import logging
import threading
from argparse import ArgumentParser

from paste.deploy import appconfig
import zmq

from rnms.config.environment import load_environment
from rnms.lib.poller import Poller
from rnms.lib.consolidate import Consolidator
from rnms.lib.sla_analyzer import SLAanalyzer
from rnms.lib import zmqmessage 

LOG_FORMAT="%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s"

class Rnmsd(object):
    """
    Master object for the Rosenberg NMS daemon. This daemon is responsible
    for starting other sub-threads either continuously or at particular times.
    """
    enable_poller = True
    enable_consolidator = True
    args = None

    def __init__(self):
        self.zmq_context = zmq.Context()
        self.zmq_poller = zmq.Poller()
        self.control_socket = zmqmessage.control_server(self.zmq_context)
    
    def run(self):
        """ The entry point for the RNMS daemon """
        self._setup_app()
        self.logger = logging.getLogger('rnms')

        self.poller = Poller(zmq_context=self.zmq_context)
        poller_thread = threading.Thread(target=self.poller.main_loop)
        poller_thread.start()

        self.consolidator = Consolidator(zmq_context=self.zmq_context, do_once=False)
        consolidator_thread = threading.Thread(target=self.consolidator.consolidate, name='consolidator')
        consolidator_thread.start()

        self.sla_analyzer = SLAanalyzer(zmq_context=self.zmq_context, do_once=False)
        sla_analyzer_thread = threading.Thread(target=self.sla_analyzer.analyze, name='sla_analyzer')
        sla_analyzer_thread.start()
        
        # main loop
        while True:
            try:
                self.zmq_poller.poll(1000)
            except KeyboardInterrupt:
                self._shutdown()
                return
            if not poller_thread.is_alive():
                self.logger.critical('poller has died')

    def _setup_app(self):
        """ Parses command line arguments and does inital setup """
        parser = ArgumentParser()
        parser.add_argument("-c", "--conf_file", help="configuration to use", default="development.ini")
        parser.add_argument("-d", "--debug", action='store_true', help="turn on debugging")
        parser.add_argument("-q", "--quiet", action='store_true', help="critical messages only")
        parser.add_argument("-v", "--verbosity", action='store_true', help="verbose messages")
        self.args = parser.parse_args()
        self._set_logging()
        conf = appconfig('config:' + os.path.abspath(self.args.conf_file))
        load_environment(conf.global_conf, conf.local_conf)

    def _set_logging(self):
        logging_level = logging.WARNING
        if self.args.quiet == True:
            logging_level = logging.CRITICAL
        elif self.args.debug == True:
            logging_level = logging.DEBUG
        elif self.args.verbosity == True:
            logging_level = logging.INFO
        
        logging.basicConfig(level=logging_level, format=LOG_FORMAT)

    def _shutdown(self):
        """ Method that is called to shutdown the daemon """
        self.control_socket.send(zmqmessage.IPC_END)
