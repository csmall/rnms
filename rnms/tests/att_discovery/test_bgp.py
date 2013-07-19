# -*- coding: utf-8 -*-
"""Test suite for BGP Attribute Discovery """
from nose.tools import eq_

from rnms.tests.att_discovery import AttDiscTest

from rnms.lib.att_discovers.bgp import discover_bgp_peers, cb_bgp_peers

class TestBGP(AttDiscTest):
    def test_none(self):
        """ BGP disc callback with None has no peers """
        self.check_callback_none(cb_bgp_peers)
    
    def test_empty(self):
        """ BGP disc callback with empty dict has no peers """
        self.check_callback_empty(cb_bgp_peers, 4)

    def test_bgp_peer_single(self):
        """ BGP discovery finds one peer """
        values = [{'192.0.2.250': '203.0.113.1'}, {'192.0.2.250': '6'}, {'192.0.2.250': '0.0.0.0'}, {'192.0.2.250': '192.0.2.250'}, {'192.0.2.250': '65531'}]
        self.callback(cb_bgp_peers, values)
        self.assert_result_count(1)
        self.assert_result_indexes(('192.0.2.250',))
        self.assert_result_display_names(('192.0.2.250',))
        self.assert_result_fields('local', {'192.0.2.250': '0.0.0.0'})
        self.assert_result_fields('asn', {'192.0.2.250': 'AS 65531'})

    def test_bgp_peer_down(self):
        """ BGP discovery finds one down peer """
        values = [{'192.0.2.250': '203.0.113.1'}, {'192.0.2.250': '2'}, {'192.0.2.250': '0.0.0.0'}, {'192.0.2.250': '192.0.2.250'}, {'192.0.2.250': '65531'}]
        self.callback(cb_bgp_peers, values)
        self.assert_result_count(1)
        self.assert_oper_state({'192.0.2.250': 'down'})

    def test_discover_bgp_peer(self):
        """ BGP discovery calls snmp correctly """
        eq_(discover_bgp_peers(*self.discover_args), True)
        self.assert_snmp_table_called()

