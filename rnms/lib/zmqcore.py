# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
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
import time

from random import randint

from errno import ECONNRESET, ENOTCONN, ESHUTDOWN, EBADF, ECONNABORTED, EPIPE

_DISCONNECTED = frozenset((ECONNRESET, ENOTCONN, ESHUTDOWN,
                           ECONNABORTED, EPIPE, EBADF))


def set_id(zsocket):
    identity = "%04x-%04x" % (randint(0, 0x10000), randint(0, 0x10000))
    zsocket.setsockopt(zmq.IDENTITY, identity)


class ZmqCore(object):

    def __init__(self):
        self.socket_map = {}
        self.zmq_map = {}
        self.zmq_poller = zmq.Poller()

    def register_zmq(self, sock, read_cb):
        """ Zero MQ sockets that want to be called back on data that is
        received using this poller need to register here
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
        One-shot poller for all of the normal and ZeroMQ sockets,
        timeout is just like the select timeout.  normal sockets
        need to use the Dispatcher as found in this module for it
        to work
        """
        # ZMQ objects should of already registered here
        if self.zmq_map == {} and self.socket_map == {}:
            try:
                time.sleep(timeout)
            except KeyboardInterrupt:
                return False
            return True

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

        for sock, event in events.items():
            if type(sock) == int:
                try:
                    obj = self.socket_map[sock]
                except KeyError:
                    self.unregister_sock(sock)
                else:
                    if event & zmq.POLLIN:
                        obj.handle_read_event()
                    if event & zmq.POLLOUT:
                        obj.handle_write_event()
                    if event & zmq.POLLERR:
                        obj.handle_close()
            else:
                cb_func = self.zmq_map[sock]
                if event == zmq.POLLIN:
                    cb_func(sock)
        return True


class Dispatcher(asyncore.dispatcher, object):

    def __init__(self, zmq_core):
        self.zmq_core = zmq_core
        asyncore.dispatcher.__init__(self, map=zmq_core.socket_map)

    def close(self):
        if self._fileno is not None:
            self.zmq_core.unregister_sock(self._fileno)
        asyncore.dispatcher.close(self)
