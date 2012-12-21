# -*- coding: utf-8 -*-
"""
Functional test suite for the TCP client

"""
import socket
import asyncore

from nose.tools import assert_true, nottest, eq_

from rnms.lib.tcpclient import TCPClient

class DummyHost(object):
    mgmt_address = ''
    community_ro = {}
    def __init__(self, ip):
        self.mgmt_address = ip

def my_callback(host, response, connect_time, error, obj, **kw):
    results = obj.results
    results['response'] = response
    results['connect_time'] = connect_time
    results['error'] = error


class TestTCP(object):
    """ Base unit for TCP client testing """

    def setUp(self):
        self.tcp_client = TCPClient()
        self.results = {}

    def poll(self):
        while self.tcp_client.poll():
            asyncore.poll(0.2)

    def test_noconnect(self):
        """ Connect to no route to host """
        host = DummyHost('172.16.242.250')
        assert(self.tcp_client.get_tcp(host, 1234, '', 0, my_callback, obj=self))
        self.poll()
        eq_(self.results['error'][0], 113)

    def test_noconnect2(self):
        """ Connect to no route to host """
        host = DummyHost('192.168.100.45')
        assert(self.tcp_client.get_tcp(host, 1234, '', 0, my_callback, obj=self))
        self.poll()
        eq_(self.results['error'][0], 113)

    def test_connrefused(self):
        """ Connection refused to bad ports """
        host = DummyHost('127.0.0.1')
        assert(self.tcp_client.get_tcp(host, 9999, 'HELO foo', 0, my_callback, obj=self))
        self.poll()
        eq_(self.results['error'][0], 111)

    def test_okipv4(self):
        """ An open port gets data """
        host = DummyHost('127.0.0.1')
        assert(self.tcp_client.get_tcp(host, 25, 'HELO foo', 1, my_callback, obj=self))
        self.poll()
        eq_(self.results['error'],None)

    def test_okipv6(self):
        """ IPv6 host connect """
        host = DummyHost('::1')
        assert(self.tcp_client.get_tcp(host, 25, 'HELO foo', 1, my_callback, obj=self))
        self.poll()
        eq_(self.results['error'],None)

    def test_far_host(self):
        """ Far host has connect time """
        host = DummyHost('gmail-smtp-in.l.google.com')
        assert(self.tcp_client.get_tcp(host, 25, '', 1, my_callback, obj=self))
        self.poll()
        eq_(self.results['error'],None)
        assert(self.results['connect_time'].total_seconds > 0.0)

