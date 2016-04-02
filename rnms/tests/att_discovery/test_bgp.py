# -*- coding: utf-8 -*-
"""Test suite for BGP Attribute Discovery """
from nose.tools import eq_

from rnms.tests.att_discovery import AttDiscTest

from rnms.lib.discovery.plugins.attributes.bgp\
    import discover_bgp_peers, cb_bgp_peers


class TestBGP(AttDiscTest):
    def test_none(self):
        """ BGP disc callback with None has no peers """
        self.check_callback_none(cb_bgp_peers)

    def test_empty(self):
        """ BGP disc callback with empty dict has no peers """
        self.check_callback_empty(cb_bgp_peers, 4)

    def test_bgp_peer_single(self):
        """ BGP discovery finds one peer """
        values = [['6', '1.1.1.1', '2.2.2.2', '65531'], ]
        self.callback(cb_bgp_peers, values)
        self.assert_result_count(1)
        self.assert_result_indexes(('2.2.2.2',))
        self.assert_result_display_names(('2.2.2.2',))
        self.assert_result_fields('local', {'2.2.2.2': '1.1.1.1'})
        self.assert_result_fields('asn', {'2.2.2.2': 'AS 65531'})

    def test_bgp_peer_down(self):
        """ BGP discovery finds one down peer """
        values = [['2', '1.1.1.1', '2.2.2.2', '65531'], ]
        self.callback(cb_bgp_peers, values)
        self.assert_result_count(1)
        self.assert_oper_state({'2.2.2.2': 'down'})

    def test_discover_bgp_peer(self):
        """ BGP discovery calls snmp correctly """
        eq_(discover_bgp_peers(*self.discover_args), True)
        self.assert_snmp_table_called()
