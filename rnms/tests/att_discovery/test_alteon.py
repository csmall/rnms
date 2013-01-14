# -*- coding: utf-8 -*-
"""Test suite for Alteon Attribute Discovery """
from nose.tools import eq_

from rnms import model
from rnms.tests.att_discovery import AttDiscTest
from rnms.lib import states

from rnms.lib.att_discovers.alteon import discover_alteon_realservers, cb_alteon_realservers

class TestAlteonRealServer(AttDiscTest):
    def test_none(self):
        """ Alteon RServer callback with None has no peers """
        self.check_callback_none(cb_alteon_realservers)

    def test_empty(self):
        """ Alteon RServer callback with empty dict has no peers """
        self.check_callback_empty(cb_alteon_realservers, 6)

    def test_single_rserver(self):
        """ Alteon Rserver finds one real server """
        values = [{'1': '1'}, {'1': '192.0.2.1'}, {'1': '12345'}, {'1': '2'}, {'1': 'realhost'}, {'1': '2'},]
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_result_indexes(('1',))
        self.assert_result_display_names(('192.0.2.1',))
        self.assert_result_fields('max_connections', {'1': '12345'})
        self.assert_result_fields('hostname', {'1': 'realhost'})
        self.assert_oper_state({'1': states.STATE_UP})
        self.assert_admin_state({'1': states.STATE_UP})
    
    def test_missing_ipaddress(self):
        """ Alteon Rserver mising ipaddr skips entry """
        values = [{'1': '1'}, {}, {'1': '12345'}, {'1': '2'}, {'1': 'realhost'}, {'1': '2'},]
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(0)
    
    def test_missing_missing_admin(self):
        """ Alteon Rserver missing admin uses default up """
        values = [{'1': '1'}, {'1': '192.0.2.1'}, {'1': '12345'}, {}, {'1': 'realhost'}, {'1': '2'},]
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_admin_state({'1': states.STATE_UP})
    
    def test_missing_missing_oper(self):
        """ Alteon Rserver missing oper uses default up """
        values = [{'1': '1'}, {'1': '192.0.2.1'}, {'1': '12345'}, {'1': '2'}, {'1': 'realhost'}, {},]
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_oper_state({'1': states.STATE_UP})
    
    def test_single_admin_down_rserver(self):
        """ Alteon Rserver finds one real server admin down """
        values = [{'1': '1'}, {'1': '192.0.2.1'}, {'1': '12345'}, {'1': '1'}, {'1': 'realhost'}, {'1': '2'},]
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_oper_state({'1': states.STATE_UP})
        self.assert_admin_state({'1': states.STATE_DOWN})
    
    def test_single_oper_down_rserver(self):
        """ Alteon Rserver finds one real server oper down """
        values = [{'1': '1'}, {'1': '192.0.2.1'}, {'1': '12345'}, {'1': '2'}, {'1': 'realhost'}, {'1': '1'},]
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_oper_state({'1': states.STATE_DOWN})
        self.assert_admin_state({'1': states.STATE_UP})

    def test_discover_alteon_rserver(self):
        """ Alteon Real Server calls snmp correctly """
        eq_(discover_alteon_realservers(self.test_host, **self.discover_kwargs), True)
        self.assert_snmp_table_called()
