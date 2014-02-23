# -*- coding: utf-8 -*-
"""Test suite for SNMP SAAgent Pollers """
from nose.tools import assert_false, assert_true

#from rnms import model
from rnms.tests.pollers import PollerTest

from rnms.lib.poller.plugins.cisco_saagent import poll_cisco_saagent, cb_jitter,\
    cb_packetloss


class TestSAAgentPoller(PollerTest):
    def test_poller_empty(self):
        """ saagent poller with no params returns false """
        assert_false(poll_cisco_saagent(self.poller_buffer, '',
                     **self.test_kwargs))

    def test_poller_badparam(self):
        """ saagent poller with bad parameters """
        assert_false(poll_cisco_saagent(self.poller_buffer, 'foo|bar',
                     **self.test_kwargs))

    def test_poller_ok(self):
        """ saagent poller calls snmp_table correctly """
        assert_true(poll_cisco_saagent(self.poller_buffer, '42|fwd_jitter',
                    **self.test_kwargs),)
        self.assert_get_list_called(
            cb_jitter, {},
            oid=[
                (1, 3, 6, 1, 4, 1, 9, 9, 42, 1, 5, 2, 1, 8, 42),
                (1, 3, 6, 1, 4, 1, 9, 9, 42, 1, 5, 2, 1, 9, 42),
                (1, 3, 6, 1, 4, 1, 9, 9, 42, 1, 5, 2, 1, 13, 42),
                (1, 3, 6, 1, 4, 1, 9, 9, 42, 1, 5, 2, 1, 14, 42)],)

    def test_cb_jitter_none(self):
        """ PollCB jitter with None returned """
        self.assert_callback_none_none(cb_jitter)

    def test_cb_packetloss_none(self):
        """ PollCB packetlos with None returned """
        self.assert_callback_none_none(cb_packetloss)
