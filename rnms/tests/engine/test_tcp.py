# -*- coding: utf-8 -*-
"""
Functional test suite for the TCP client

"""
import mock
import errno

from nose.tools import eq_

from rnms.lib.tcpclient import TCPClient
from rnms.lib import zmqcore


class TestTCP(object):
    """ Base unit for TCP client testing """

    def assert_cb_error_code(self, errcode):
        eq_(self.my_callback.call_count, 1)
        if errcode is None:
            eq_(self.my_callback.call_args[0][1], None)
        else:
            eq_(self.my_callback.call_args[0][1][0], errcode)

    def setUp(self):
        self.zmq_core = zmqcore.ZmqCore()
        self.tcp_client = TCPClient(self.zmq_core)
        self.results = {}
        self.my_callback = mock.Mock()

    def poll(self):
        while self.tcp_client.poll() > 0:
            self.zmq_core.poll(0.2)

    def test_noconnect(self):
        """ Connect to no route to host """
        assert(self.tcp_client.get_tcp(
            '172.16.242.250', 1234, '', 0, self.my_callback, obj=self))
        self.poll()
        self.assert_cb_error_code(errno.EHOSTUNREACH)

    def test_connrefused(self):
        """ Connection refused to bad ports """
        assert(self.tcp_client.get_tcp(
            '127.0.0.1', 9999, 'HELO foo', 0, self.my_callback, obj=self))
        self.poll()
        self.assert_cb_error_code(errno.ECONNREFUSED)

    def test_okipv4(self):
        """ An open port gets data """
        assert(self.tcp_client.get_tcp(
            '127.0.0.1', 25, 'HELO foo', 1, self.my_callback, obj=self))
        self.poll()
        self.assert_cb_error_code(None)

    def test_okipv6(self):
        """ IPv6 host connect """
        assert(self.tcp_client.get_tcp(
            '::1', 25, 'HELO foo', 1, self.my_callback, obj=self))
        self.poll()
        self.assert_cb_error_code(None)

    def test_far_host(self):
        """ Far host has connect time """
        assert(self.tcp_client.get_tcp(
            '127.0.0.1', 22, '', 1, self.my_callback, obj=self))
        self.poll()
        self.assert_cb_error_code(None)
        assert(self.my_callback.call_args[0][0][1].total_seconds() > 0.0)
