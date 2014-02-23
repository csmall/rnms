# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013-2014 Craig Small <csmall@enc.com.au>
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
"""Test suite for Reach Pollers """
from nose.tools import eq_
import mock

from rnms import model
from rnms.tests.pollers import PollerTest
from rnms.lib import states

from rnms.lib.pingclient import PingClient
from rnms.lib.poller.plugins.reach import poll_reach_ping, cb_reach_ping

field_values = {}
def field_value(att_id, fname):
    try:
        return field_values[fname]
    except:
        return None


class TestReachPoller(PollerTest):

    def setUp(self):
        super(TestReachPoller, self).setUp()

        self.ping_client = mock.MagicMock(spec_set=PingClient)
        self.ping_client.ping_host = mock.Mock(return_value=True)
        self.pobj.ping_client = self.ping_client


    def assert_ping_host_called(self, cb_fun, num_pings, interval):
        """ Check the PingClient ping_host method was called """
        self.ping_client.ping_host.assert_called_once_with(self.test_host_ip, cb_fun, num_pings, interval, pings=num_pings, **self.test_kwargs)

    def test_poll_reach_ping_ok(self):
        """ poll_reach_ping calls ping client correctly """
        self.set_attribute_fields({'pings': '45', 'interval': '67'})
        eq_(poll_reach_ping(self.poller_buffer, '', **self.test_kwargs), True)
        self.assert_ping_host_called(cb_reach_ping, 45,67)

    def test_poll_reach_ping_no_numping(self):
        """ poll_reach_ping with missing ping count  calls ping client correctly """
        self.set_attribute_fields({'interval': '67'})
        eq_(poll_reach_ping(self.poller_buffer, '', **self.test_kwargs), True)
        self.assert_ping_host_called(cb_reach_ping, 10,67)

    def test_poll_reach_ping_nointerval(self):
        """ poll_reach_ping with no interval calls ping client correctly """
        self.set_attribute_fields({'pings': '45'})
        eq_(poll_reach_ping(self.poller_buffer, '', **self.test_kwargs), True)
        self.assert_ping_host_called(cb_reach_ping, 45,300)

    def test_poll_reach_ping_badping(self):
        """ poll_reach_ping wth bad ping field calls ping client correctly """
        self.set_attribute_fields({'pings': 'FOOO', 'interval': '67'})
        eq_(poll_reach_ping(self.poller_buffer, '', **self.test_kwargs), True)
        self.assert_ping_host_called(cb_reach_ping, 10,67)

    def test_poll_reach_ping_badinterval(self):
        """ poll_reach_ping with bad interval calls ping client correctly """
        self.set_attribute_fields({'pings': '45', 'interval': 'FOO'})
        eq_(poll_reach_ping(self.poller_buffer, '', **self.test_kwargs), True)
        self.assert_ping_host_called(cb_reach_ping, 45,300)

    def test_cb_none(self):
        """ cb_reach_ping with no values """
        cb_reach_ping(None, None, **self.test_kwargs)
        self.assert_callback(None)

    def test_cb_ping(self):
        """ cb_reach_ping """
        cb_reach_ping((1.1, 2.2), None, **self.test_kwargs)
        self.assert_callback((1.1, 2.2))

