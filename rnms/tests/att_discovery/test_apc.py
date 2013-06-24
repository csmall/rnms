# -*- coding: utf-8 -*-
"""Test suite for APC UPS Attribute Discovery """
from nose.tools import eq_

from rnms.tests.att_discovery import AttDiscTest

from rnms.lib.att_discovers.apc import discover_apc, cb_apc


class TestApcDiscover(AttDiscTest):

    def test_discover_apc(self):
        """ APC discovery calls snmp get correctly """
        eq_(discover_apc(*self.discover_args), True)
        self.assert_snmp_get_called(oid_count=3)

    def test_cb_none(self):
        """ APC discovery callback with None has no Attributes """
        self.check_callback_none(cb_apc)

    def test_cb_empty(self):
        """ APC discovery callback with empty has no Attributes """
        self.check_callback_empty(cb_apc, 3)

    def test_cb_single(self):
        """ APC discovery callback finds single item """
        values = {'1.1.1.0': 'Test Device', '1.1.2.0': 'description', '2.1.1.0': 2}
        cb_apc(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_result_indexes(('1',))
        self.assert_result_display_names(('Test Device',))
        self.assert_oper_state({'1':'up'})
    
    def test_cb_single_down1(self):
        """ APC discovery callback finds single item down with state 1 """
        values = {'1.1.1.0': 'Test Device', '1.1.2.0': 'description', '2.1.1.0': 1}
        cb_apc(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_result_indexes(('1',))
        self.assert_result_display_names(('Test Device',))
        self.assert_oper_state({'1':'down'})
    
    def test_cb_single_down3(self):
        """ APC discovery callback finds single item down with state 3 """
        values = {'1.1.1.0': 'Test Device', '1.1.2.0': 'description', '2.1.1.0': 3}
        cb_apc(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_result_indexes(('1',))
        self.assert_result_display_names(('Test Device',))
        self.assert_oper_state({'1':'down'})
