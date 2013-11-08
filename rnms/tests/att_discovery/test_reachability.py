# -*- coding: utf-8 -*-
"""Test suite for reachability discovery """
import mock
from nose.tools import assert_true, assert_false

from rnms.tests.att_discovery import AttDiscTest
from rnms.lib.att_discovers.reachability import discover_reachability


class TestReachability(AttDiscTest):

    def test_disc_bad(self):
        """ Disc reachabiliy calls ping_client  """
        self.dobj.ping_client = mock.Mock()
        self.dobj.ping_client.get_fping = mock.Mock(return_value=None)
        assert_true(discover_reachability(*self.discover_args))
        self.assert_callback({})

    def test_disc_ok(self):
        """ Disc reachabiliy calls ping_client  """
        self.dobj.ping_client = mock.Mock()
        self.dobj.ping_client.get_fping = mock.Mock(return_value=1)
        assert_true(discover_reachability(*self.discover_args))
        self.assert_result_count(1)
