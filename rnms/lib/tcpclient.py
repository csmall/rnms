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
import socket
import datetime
import logging
import os
import string
from errno import errorcode

from rnms.lib import zmqcore

logger = logging.getLogger('TCPClient')

""" TCP Client """

class TCPClientError(Exception):
    pass

class TCPClient():
    """
    TCP Client is the Base Class to make TCP control queries.
    Each request needs its own dispatcher
    """
    zmq_core = None

    def __init__(self, zmq_core):
        self.dispatchers = []
        self.zmq_core = zmq_core

    def get_tcp(self, ipaddr, port, send_msg, max_bytes, cb_fun, **kwargs):
        """
        Query a host with the given TCP port and collect the number
        of bytes. Returns a dictionary to the cb_fun 
        """
        new_dispatcher = TCPDispatcher(self.zmq_core)
        if new_dispatcher.send_message(ipaddr, port, send_msg, max_bytes, cb_fun, **kwargs) == True:
            self.dispatchers.append(new_dispatcher)
            return True
        return False

    def poll(self):
        # Remove the old ones first
        retval = 0
        for disp_id,disp in enumerate(self.dispatchers):
            if not disp.connecting and not disp.connected:
                del self.dispatchers[disp_id]
            if disp.poll():
                retval += 1
        return retval

class TCPDispatcher(zmqcore.Dispatcher):
    """
    Dispatcher for each TCP queries
    """
    connect_timeout = 10
    total_timeout = 20
    connect_time = None
    responded = False

    def _set_error(self, err, errmsg=''):
        """ Set the error for this object, if errmsg is not set try to
        find it if it a usual one
        """
        if errmsg == '':
            try:
                errmsg = os.strerror(err)
            except (TypeError, ValueError, OverflowError, NameError):
                try:
                    errmsg = errorcode[err]
                except (KeyError,NameError):
                    errmsg = 'Unknown Error {}'.format(err)
        self.error = (err, errmsg)




    def send_message(self, ipaddr, port, send_msg, max_bytes, cb_fun, **kwargs):
        try:
            addrinfo = socket.getaddrinfo(ipaddr, port)[0]
        except socket.gaierror:
            logger.error("Cannot resolve %s:%s", ipaddr, port)
            return False
        address_family, sockaddr = addrinfo[0], addrinfo[4]
        self.create_socket(address_family, socket.SOCK_STREAM)
        self.outbuf = send_msg
        self.inbuf = ''
        self.max_bytes = max_bytes
        self.cb_fun = cb_fun
        self.kwargs = kwargs
        self.error = None
        self.start_connect = datetime.datetime.now()
        try:
            self.connect(sockaddr)
        except socket.error as err:
            self._set_error(err)
            self.handle_close()
        return True

    def handle_connect_event(self):
        err = self.socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if err != 0:
            self._set_error(err)
            self.handle_close()
        else:
            self.connect_time = datetime.datetime.now() - self.start_connect
            self.connected = True
            self.connecting = False
            if self.max_bytes is None:
                self.handle_close()

    def handle_close(self):
        self.close()
        self._parse_response()

    def handle_read(self):
        try:
            self.inbuf += self.recv(8192)
        except socket.error as err:
            self._set_error(err.errno, err.strerror)
            self.handle_close()
        else:
            if self.max_bytes is not None and self.max_bytes != 0 and len(self.inbuf) > self.max_bytes:
                self.handle_close()

    def readable(self):
        return (self.max_bytes is not None)

    def writable(self):
        return (len(self.outbuf) > 0)

    def handle_write(self):
        sent = self.send(self.outbuf)
        self.outbuf = self.outbuf[sent:]

    def _parse_response(self):
        if self.responded == False:
            filtered_buf = ''.join([c for c in self.inbuf if c in string.printable])
            print self.kwargs
            self.cb_fun((filtered_buf,self.connect_time), self.error, **self.kwargs)
            self.responded = True

    def poll(self):
        now = datetime.datetime.now()
        if self.connecting:
            if (now - self.start_connect).total_seconds() > self.connect_timeout:
                self._set_error(-1, 'timed out connecting to host')
                self.handle_close()
                return False
        else:
            if (now - self.start_connect).total_seconds() > self.total_timeout:
                self._set_error(-1, 'timed out getting data from host')
                self.handle_close()
                return False
        return True

