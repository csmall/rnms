# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2015 Craig Small <csmall@enc.com.au>
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
""" Test suite for the Poller and PollerSet model in RoseNMS"""
from nose.tools import eq_
from mock import MagicMock

from rnms import model
from rnms.lib.zmqcore import ZmqCore
from rnms.lib.poller import CacheHost
from rnms.lib.snmp.engine import SNMPEngine
from rnms.lib.snmp.scheduler import SNMPScheduler


class TestSnmpEngine(object):
    test_host_id = 123
    test_host_ip = '127.0.0.2'

    def setUp(self):
        mock_zmq_core = MagicMock(spec=ZmqCore)
        mock_zmq_core.socket_map = MagicMock()
        mock_logger = MagicMock()
        self.obj = SNMPEngine(mock_zmq_core, mock_logger)
        self.obj.scheduler = MagicMock(spec_set=SNMPScheduler)
        self.obj.scheduler.request_add = MagicMock()
        self.obj.transport_dispatcher = MagicMock()

        self.test_host = MagicMock(spec_set=CacheHost, name='testhost')
        self.test_host.id = self.test_host_id
        self.test_host.mgmt_address = self.test_host_ip
        self.test_community = MagicMock(spec_set=model.SnmpCommunity)
        self.test_community.version = 2
        self.test_community.community = 'public'
        self.test_host.ro_community = self.test_community

        self.test_callback = MagicMock()

    def assert_scheduler_add_called(self, call_count):
        eq_(self.obj.scheduler.request_add.call_count, call_count)

    def assert_request_callback(self):
        eq_(self.obj.scheduler.request_add.call_args[0][0]._callback,
            self.test_callback)

    def assert_request_oid_callback(self):
        for oid in self.obj.scheduler.request_add.call_args[0][0].oids:
            eq_(oid.cb_func, self.test_callback)

    def assert_oid_filter(self, filter_type):
        eq_(self.obj.scheduler.request_add.call_args[0][0].oids[0].filter_,
            filter_type)

    def test_get_int(self):
        """ SNMPEngine: get_int """
        self.obj.get_int(self.test_host, None, self.test_callback)
        self.assert_scheduler_add_called(1)
        self.assert_request_oid_callback()
        self.assert_oid_filter('int')

    def test_get_str(self):
        """ SNMPEngine: get_str """
        self.obj.get_str(self.test_host, None, self.test_callback)
        self.assert_scheduler_add_called(1)
        self.assert_request_oid_callback()
        self.assert_oid_filter('str')

    def test_get_list(self):
        """ SNMPEngine: get_list """
        test_oids = [1, 2, 3]
        self.obj.get_list(self.test_host, test_oids, self.test_callback)
        self.assert_scheduler_add_called(1)
        self.assert_request_callback()

    def test_get_many(self):
        """ SNMPEngine: get_many """
        test_oids = [1, 2, 3]
        self.obj.get_many(self.test_host, test_oids, self.test_callback)
        self.assert_scheduler_add_called(1)
        self.assert_request_oid_callback()

    def test_get_table(self):
        """ SNMPEngine: get_table """
        test_oids = [1, 2, 3]
        self.obj.get_table(self.test_host, test_oids, self.test_callback)
        self.assert_scheduler_add_called(1)
        self.assert_request_callback()

    def test_request_finished(self):
        """ SNMPEngine: request_finished """
        self.obj.active_requests = {123: None, 456: None}
        self.obj._request_finished(123)
        eq_(self.obj.scheduler.request_received.call_count, 1)
        eq_(self.obj.scheduler.request_received.call_args[0], (123, ))
        eq_(len(self.obj.active_requests), 1)
        self.obj.active_requests = {}
