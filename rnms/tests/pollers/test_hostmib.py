# -*- coding: utf-8 -*-
"""Test suite for SNMP HostMIB Pollers """
from nose.tools import assert_true

#  from rnms import model
from rnms.tests.pollers import PollerTest

from rnms.lib.poller.plugins.hostmib import poll_hostmib_apps,\
    cb_hostmib_apps, poll_hostmib_perf, cb_hostmib_perf


class TestHostMIBPoller(PollerTest):
    def test_poller_ok(self):
        """ HostMib apps poll """
        assert_true(poll_hostmib_apps(self.poller_buffer, '',
                    **self.test_kwargs))
        self.assert_get_table_called(
            cb_hostmib_apps, {'with_oid': 1},
            oid=((1, 3, 6, 1, 2, 1, 25, 4, 2, 1, 2),)
            )

    def test_cbapp_none(self):
        """ PollCB hostmib app with None returned """
        self.assert_callback_none(cb_hostmib_apps)

    def test_cbapp_notfound(self):
        """ PollCB hostmib app with no process"""
        self.assert_callback_value(
            cb_hostmib_apps,
            [[('1', 'one')], [('200', 'some attribute')],
                [('201', 'other attribute')], [('202', 'other attribute')],
                [('3000', 'three')]],
            ('not_running', 0, []))

    def test_cbapp_found(self):
        """ PollCB hostmib app with found process"""
        self.assert_callback_value(
            cb_hostmib_apps,
            [[('1', 'one')], [('200', 'test attribute')],
                [('201', 'test attribute')], [('202', 'test attribute')],
                [('3000', 'three')]],
            ('running', 3, [200, 201, 202]))

    def test_pollperf_badbuf(self):
        """ Poller HostMIB perf with empty buffer """
        assert_true(poll_hostmib_perf(self.poller_buffer, '',
                    **self.test_kwargs))
        self.assert_callback(0)

    def test_pollperf_ok(self):
        """ Poller HostMIB perf with correct buffer """
        poller_buffer = {'pids': [1, 20, 300]}
        assert_true(poll_hostmib_perf(poller_buffer, '',
                    **self.test_kwargs))
        self.assert_get_list_called(
            cb_hostmib_perf, {},
            oid=[
                (1, 3, 6, 1, 2, 1, 25, 5, 1, 1, 2, 1),
                (1, 3, 6, 1, 2, 1, 25, 5, 1, 1, 2, 20),
                (1, 3, 6, 1, 2, 1, 25, 5, 1, 1, 2, 300),
                ])

    def test_cbperf_none(self):
        """ PollCB HostMIB perf returned None """
        self.assert_callback_value(cb_hostmib_perf, None, 0)

    def test_cbperf_values(self):
        """ PollCB HostMIB perf returned correct values """
        self.assert_callback_value(cb_hostmib_perf, [1, 2, 3], 6)
