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
"""Test suite for TCP Pollers """
import datetime

from nose.tools import eq_, assert_true
import mock

from rnms import model
from rnms.tests.pollers import PollerTest
from rnms.lib import states
from rnms.lib.tcpclient import TCPClient
from rnms.lib.pollers.tcp import poll_tcp_status, cb_tcp_status,\
        poll_snmp_tcp_established, cb_snmp_tcp_established,\
        poll_tcp_content

class TestTCPPoller(PollerTest):

    def setUp(self):
        super(TestTCPPoller, self).setUp()
        self.tcp_client = mock.MagicMock(spec_set=TCPClient)
        self.tcp_client.get_tcp = mock.Mock(return_value=True)
        self.pobj.tcp_client = self.tcp_client

    def assert_get_tcp_called(self, port, send_msg, max_bytes, cb_fun):
        self.tcp_client.get_tcp.assert_called_once_with(
            self.test_host_ip, port, send_msg, max_bytes,
            cb_fun, **self.test_kwargs)

    def test_poll_tcp_ok(self):
        """ Poller tcp_status calls tcp_get correctly """
        assert_true(poll_tcp_status(self.poller_buffer,'99', **self.test_kwargs))
        self.assert_get_tcp_called(1, ' ', None, cb_tcp_status)

    def test_poll_tcp_badbytes(self):
        """ Poller tcp_status with bad max_bytes """
        assert_true(poll_tcp_status(self.poller_buffer,'BAD', **self.test_kwargs))
        self.assert_get_tcp_called(1, ' ', None, cb_tcp_status)

    def test_cb_none(self):
        """ PollCB tcp_status with no values """
        cb_tcp_status(None, None, **self.test_kwargs)
        self.assert_callback((u'open', None, None, None))

    def test_cb_ok(self):
        """ PollCB tcp_status with correct values """
        connect_time = datetime.timedelta(0,123,456000)
        cb_tcp_status((u'Hi', connect_time), None, **self.test_kwargs)
        self.assert_callback((u'open', u'Hi', 123.456, None))

    def test_poll_tcp_estab(self):
        """ Poller tcp_established calls SNMP engine """
        assert_true(poll_snmp_tcp_established(self.poller_buffer, '',
                                             **self.test_kwargs))
        self.assert_get_table_called(cb_snmp_tcp_established,
                                    oid=((1, 3, 6, 1, 2, 1, 6, 13, 1, 1),))
    def test_cb_tcp_stabl_none(self):
        """ PollCB tcp_established with no values """
        self.assert_callback_none(cb_snmp_tcp_established)

    def test_cb_tcp_estab_none(self):
        """ PollCB tcp_established with correct values """
        values = (({
            '127.0.0.1.1.11.11.11.11.1100': '5',
            '127.0.0.1.9.11.11.11.11.1100': '5',
            '127.0.0.1.1.21.21.21.21.2100': '5',
            '127.0.0.1.1.31.21.21.21.2100': '2',
            '127.0.0.1.1.41.21.21.21.2100': '5',
        }),)
        cb_snmp_tcp_established(values, None, **self.test_kwargs)
        self.assert_callback(3)

    def test_poll_tcp_content_none(self):
        """ Poller tcp_content with no poller buffer """
        assert_true(poll_tcp_content(self.poller_buffer, '',
                                     **self.test_kwargs))
        self.assert_callback(((u'valid', u'not checked')))
