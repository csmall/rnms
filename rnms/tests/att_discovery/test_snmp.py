# -*- coding: utf-8 -*-
"""Test suite for SNMP Attribute Discovery """
from nose.tools import eq_

from rnms.tests.att_discovery import AttDiscTest

from rnms.lib.att_discovers.snmp import discover_snmp_simple, cb_snmp_simple

class TestSNMP(AttDiscTest):
    def test_discover_snmp_simple(self):
        """ snmp simple discovery calls snmp correctly """
        self.set_ad_parameters('1.2.3|Item')
        eq_(discover_snmp_simple(*self.discover_args), True)
        self.assert_snmp_get_called(oid_count=1)

    def test_simple_none(self):
        """ SNMP simple disc callback with None has no peers """
        self.test_callback_kwargs['display_name']='hello'
        self.check_callback_none(cb_snmp_simple)
    
    def test_simple_empty(self):
        """ SNMP simple disc callback with empty dict has no peers """
        self.test_callback_kwargs['display_name']='hello'
        self.check_callback_empty(cb_snmp_simple, 6)

    def test_cb_snmp_simple_single(self):
        """ SNMP simple discovery finds an item """
        values = [{'1.2.3': '1.2.3'}]
        cb_snmp_simple(values, None, display_name='Item', **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_result_indexes(('1',))
        self.assert_result_display_names(('Item',))

