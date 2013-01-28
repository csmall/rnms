# -*- coding: utf-8 -*-
"""Test suite for Apache Attribute Discovery """
from nose.tools import eq_

from rnms import model
from rnms.tests.att_discovery import AttDiscTest
from rnms.lib import states

from rnms.lib.att_discovers.apache import discover_apache, cb_apache

class TestApacheDiscovery(AttDiscTest):

    def test_disc_ok(self):
        """ Apache discovery calles tcpclient correctly """
        eq_(discover_apache(self.test_host, **self.discover_kwargs), True)
        self.assert_get_tcp_called(80, 'GET /server-status?auto HTTP/1.1\r\nHost: {}\r\n\r\n'.format(self.test_host_ip), 40, cb_apache)

    def test_cb_none(self):
        """ Apache AD with None returns None """
        self.check_callback_none(cb_apache)

    def test_cb_short(self):
        """ Apache AD with short response returns no item """
        cb_apache(('blah', 4), None, **self.test_callback_kwargs)
        self.assert_result_count(0)
    
    def test_cb_notstring(self):
        """ Apache AD with array of none returns no item """
        cb_apache((None, None), None, **self.test_callback_kwargs)
        self.assert_result_count(0)
    
    def test_cb_404(self):
        """ Apache AD with short response returns no item """
        resp = 'HTTP/1.1 404 Not Found\r\nServer: foobar/1.0.0'
        cb_apache((resp, 4), None, **self.test_callback_kwargs)
        self.assert_result_count(0)

    def test_cb_ok(self):
        """ Apache AD with correct response shows item"""
        valid_result = """HTTP/1.1 200 OK
Date: Thu, 07 Oct 1971 01:01:01 GMT
Server: Apache/2.2.22 (Debian)
Vary: Accept-Encoding
Content-Length: 437
Content-Type: text/plain; charset=ISO-8859-1

Total Accesses: 2000
Total kBytes: 8000
CPULoad: .070
Uptime: 204800
ReqPerSec: .141
BytesPerSec: 123.456
BytesPerReq: 6543.21
BusyWorkers: 8
IdleWorkers: 1
Scoreboard: _GGG.GW.G_GG_______G............................................................................................................................................................................................................................................
"""
        cb_apache((valid_result, 8), None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_result_indexes(('{}:80'.format(self.test_host_ip),))
        self.assert_result_display_names((u'Apache Information',))
