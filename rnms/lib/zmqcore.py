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
# This file is a lot like the python asyncore that appears in the core python
# libraries. That file is Copyright 1996 by Sam Rushing
"""
Basic infrastrcuture to make asynchronous sockets using the ZeroMQ polling
instead of the core one.
"""
import zmq
import asyncore

from random import randint

from errno import ECONNRESET, ENOTCONN, ESHUTDOWN, EBADF, ECONNABORTED, EPIPE

_DISCONNECTED = frozenset((ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, EPIPE,
                           EBADF))

def set_id(zsocket):
    identity = "%04x-%04x" % (randint(0, 0x10000), randint(0, 0x10000))
    zsocket.setsockopt(zmq.IDENTITY, identity)

class ZmqCore(object):

    def __init__(self):
        self.socket_map = {}
        self.zmq_map = {}
        self.zmq_poller = zmq.Poller()

    def register_zmq(self, sock, read_cb):
        """ Zero MQ sockets that want to be called back on data that is received
        using this poller need to register here
        """
        self.zmq_poller.register(sock, zmq.POLLIN)
        self.zmq_map[sock] = read_cb

    def unregister_zmq(self, sock):
        """ Unregister from this poller """
        self.zmq_poller.unregister(sock)
        del self.zmq_map[sock]

    def register_sock(self, sockfd, dispatcher):
        """ Register a regular socket """
        self.socket_map[sockfd] = dispatcher

    def unregister_sock(self, sockfd):
        """ Unregister a socket form the zmq core with the given socket
        fd """
        try:
            self.zmq_poller.unregister(sockfd)
        except KeyError:
            pass
        try:
            del self.socket_map[sockfd]
        except KeyError:
            pass

    def poll(self, timeout=0.0):
        """
        One-shot poller for all of the normal and ZeroMQ sockets, timeout is just like the
        select timeout.  normal sockets need to use the Dispatcher as found in this module for it to work
        """
        # ZMQ objects should of already registered here

        for fd, obj in self.socket_map.items():
            flags = 0
            if obj.readable():
                flags |= zmq.POLLIN
            if obj.writable():
                flags |= zmq.POLLOUT
            self.zmq_poller.register(fd, flags)
        try:
            events = dict(self.zmq_poller.poll(timeout*1000))
        except KeyboardInterrupt:
            return False

        for sock,event in events.items():
            if type(sock) == int:
                try:
                    obj =  self.socket_map[sock]
                except KeyError:
                    pass
                else:
                    if event & zmq.POLLIN:
                        obj.handle_read_event()
                    if event & zmq.POLLOUT:
                        obj.handle_write_event()
            else:
                cb_func = self.zmq_map[sock]
                if event == zmq.POLLIN:
                    cb_func(sock)
        return True

class Dispatcher(asyncore.dispatcher,object):

    def __init__(self, zmq_core):
        self.zmq_core = zmq_core
        asyncore.dispatcher.__init__(self,map=zmq_core.socket_map)

    def close(self):
        asyncore.dispatcher.close(self)
        self.zmq_core.unregister_sock(self.socket)

#class iDispatcher(object):
#    connected = False
#    connecting = False
#
#    def __init__(self, zmq_core):
#        self.zmq_core = zmq_core
#        self._fileno = None
#        self.socket = None
#    
#    def create_socket(self, family, type):
#        self.family_and_type = family, type
#        self.socket = socket.socket(family, type)
#        self.socket.setblocking(0)
#        self._fileno = self.socket.fileno()
#        self.zmq_core.register_sock(self._fileno, self)
#
#    def readable(self):
#        return True
#
#    def writable(self):
#        return True
#
#    def connect(self, address):
#        self.connected = False
#        self.connecting = True
#        try:
#            self.socket.connect(address)
#        except socket.error, why:
#            if why.args[0] in (EINPROGRESS, EALREADY, EWOULDBLOCK) \
#                or why.args[0] == EINVAL and os.name in ('nt', 'ce'):
#                    self.addr = address
#                    return
#            if why.args[0] != EISCONN:
#                raise
#        self.addr = address
#        self.handle_connect_event()
#
#    def send(self, data):
#        """ Try to send the data out the socket """
#        try:
#            return self.socket.send(data)
#        except socket.error, why:
#            if why.args[0] == EWOULDBLOCK:
#                return 0
#            elif why.args[0] in _DISCONNECTED:
#                self.handle_close()
#                return 0
#            else:
#                raise
#    def sendto(self, data, address):
#        return self.socket.sendto(data, address)
#
#    def recv(self, buffer_size):
#        try:
#            data = self.socket.recv(buffer_size)
#            if not data:
#                self.handle_close()
#                return ''
#            else:
#                return data
#        except socket.error, why:
#            if why.args[0] in _DISCONNECTED:
#                self.handle_close()
#                return ''
#            else:
#                raise
#    
#    def recvfrom(self, buffer_size=None):
#        return self.socket.recvfrom(buffer_size)
#
#    def close(self):
#        self.connected = False
#        self.connecting = False
#        self.zmq_core.unregister_sock(self._fileno)
#
#        try:
#            self.socket.close()
#        except socket.error, why:
#            if why.args[0] not in (ENOTCONN, EBADF):
#                raise
#        self._fileno = None
#        
#    def handle_read_event(self):
#        if not self.connected and self.connecting:
#            self.handle_connect_event()
#        self.handle_read()
#
#    def handle_connect_event(self):
#        err = self.socket.getsockopt(socket.SOLsocket, socket.SO_ERROR)
#        if err != 0:
#            raise socket.error(err, os.strerror(err))
#        self.handle_connect()
#        self.connected = True
#        self.connecting = False
#
#    def handle_write_event(self):
#        if not self.connected and self.connecting:
#            self.handle_connect_event()
#        self.handle_write()
#    
#        
#    def handle_read(self):
#        raise NotImplementedError('unhandled read event')
#    
#    def handle_write(self):
#        raise NotImplementedError('unhandled write event')
#
#    def handle_close(self):
#        self.close()
#
