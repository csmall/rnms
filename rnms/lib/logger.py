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
import threading
import logging
import json

import zmq

from rnms.lib import zmqmessage

class LoggingClient(object):
    """
    Returns a ZeroMQ Socket for sending messages
    """
    socket = None

    def __init__(self, context):
        self.socket = context.socket(zmq.PUSH)
        self.socket.connect(zmqmessage.LOGGER_CLIENT)

    def critical(self,*args):
        self.send(logging.CRITICAL, *args)
    def debug(self,*args):
        self.send(logging.DEBUG, *args)
    def error(self,*args):
        self.send(logging.ERROR, *args)
    def info(self,*args):
        self.send(logging.INFO, *args)
    def warning(self,*args):
        self.send(logging.WARNING, *args)
    def warn(self,*args):
        self.send(logging.WARNING, *args)

    def send(self,level, *args):
        self.socket.send(zmqmessage.IPC_LOG, zmq.SNDMORE)
        self.socket.send(str(level), zmq.SNDMORE)
        self.socket.send_json(args)

class LoggingTask(threading.Thread):
    """
    This thread is responsible for all the logging that goes on
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.name='Rnms logger'

    def run(self):
        logger = logging.getLogger('rnms')
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind(zmqmessage.LOGGER_SERVER)
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        logger.info('Logging Worker Started log level {}'.format(logging.getLevelName(logger.getEffectiveLevel())))

        while True:
            socks = dict(poller.poll())
            if socket in socks and socks[socket] == zmq.POLLIN:
                frames = socket.recv_multipart()
                if frames[0] == zmqmessage.IPC_LOG:
                    if len(frames) == 3:
                        level = int(frames[1])
                        msgs = json.loads(frames[2])
                        logger.log(level,*msgs)
        logger.info('Logging Worker Ending')

