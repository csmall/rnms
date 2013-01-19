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
"""Test suite for Apache Pollers """
from nose.tools import eq_

from rnms import model
from rnms.tests.pollers import PollerTest
from rnms.lib import states

from rnms.lib.pollers.apache import poll_apache, cb_apache

class TestApachePoller(PollerTest):
    use_tcpclient = True

    def test_poll_ok(self):
        """ poll_apache calls tcp_client correctly """
        eq_(poll_apache(self.poller_buffer, '', **self.test_kwargs), True)
        self.assert_tcp_client_called(80, 'GET /server-status?auto HTTP/1.1\r\nHost: {}\r\n\r\n'.format(self.test_host_ip), 1000, cb_apache)

    def test_cb_none(self):
        """ cb_apache receives nothing """
        cb_apache(self.test_host, None, 0, None, **self.test_kwargs)
        self.assert_callback(None)

    def test_cb_403(self):
        """ cb_apache receives error """
        cb_apache(self.test_host, 'HTTP/1.1 403 Error', 0, None, **self.test_kwargs)
        self.assert_callback(None)

    def test_cb_ok(self):
        """ cb_apache receives valid result """
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
        cb_apache(self.test_host, valid_result, len(valid_result), None, **self.test_kwargs)
        self.assert_callback(['2000', '8000', '.070', '204800', '6543.21', '8', '1'])
