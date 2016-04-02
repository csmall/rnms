# -*- coding: utf-8 -*-
"""Test suite for NTP discovery """

import mock
from nose.tools import assert_true

from rnms.tests.att_discovery import AttDiscTest
from rnms.lib.ntpclient import NTPClient
from rnms.lib.discovery.plugins.attributes.ntp_client import \
    discover_ntp_client, cb_ntp_peer_list


class TestNtp(AttDiscTest):

    def setUp(self):
        super(TestNtp, self).setUp()
        self.dobj.ntp_client = mock.MagicMock(spec_set=NTPClient)
        self.dobj.ntp_client.get_peers = mock.Mock(return_value=True)

    def test_disc_ok(self):
        """ Disc NTP calls NTPClient """
        assert_true(discover_ntp_client(*self.discover_args))
        assert_true(self.dobj.ntp_client.get_peers.called)

    def test_cb_None(self):
        """ CbDisc NTP with None """
        self.check_callback_none(cb_ntp_peer_list)

    def test_cb_empty(self):
        """ CbDisc with no peers """
        self.callback(cb_ntp_peer_list, [])
        self.assert_callback({})

    def test_cb_ok_up(self):
        """ CbDisc with up peers """
        values = [(46962, 6), (46963, 0), (46964, 0)]
        self.callback(cb_ntp_peer_list, values)
        self.assert_result_count(1)
        self.assert_oper_state({'1': 'up'})

    def test_cb_ok_down(self):
        """ CbDisc with up peers """
        values = [(46962, 0), (46963, 0), (46964, 0)]
        self.callback(cb_ntp_peer_list, values)
        self.assert_result_count(1)
        self.assert_oper_state({'1': 'down'})
