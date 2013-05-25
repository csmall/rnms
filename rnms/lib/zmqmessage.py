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
""" Messages for the IPC """

import zmq

LOGGER_SERVER = 'tcp://*:5000'
LOGGER_CLIENT = 'tcp://localhost:5000'
RRD_ROUTER = 'tcp://*:5001'
RRD_WORKER = 'tcp://localhost:5001'
CONTROL_SERVER = 'tcp://*:5002'
CONTROL_CLIENT = 'tcp://localhost:5002'

# The inter-process sockets
CONTROL_SOCKET = 'inproc://control'
LOGGER_SOCKET = 'inproc://logger'
RRDWORKER_SOCKET = 'inproc://rrdworker'

IPC_END     = "\x01" # Sent from main process, the sub-process will die
INIT        = "\x02" # Child init sent to parent
CONF        = "\x03" # Parent sending config to child
READY       = "\x04" # Config/job consumed
IPC_INFO_REQ    = '\x05' # Info request
IPC_INFO_REP    = '\x06' # Info reply



IPC_LOG     = "\x10" # Sent to logger, log this message
RRD_UPDATE  = "\x11" # Sent to rrdworker - rrd updates


# Common tasks
def init_and_config(socket):
    """
    Send the init message and block until we get the config message
    """
    socket.send(INIT)
    frames = socket.recv_multipart()
    if frames[0] != CONF or len(frames) != 2:
        return None
    return frames[1]

def control_server(context):
    """ Setup the control server socket that the main thread runs to
    control others 
    """
    socket = context.socket(zmq.PUB)
    socket.bind(CONTROL_SOCKET)
    return socket

def control_client(context):
    """ Control socket for clients to listen on and be controlled """
    socket = context.socket(zmq.SUB)
    socket.connect(CONTROL_SOCKET)
    socket.setsockopt(zmq.SUBSCRIBE, '')
    return socket
