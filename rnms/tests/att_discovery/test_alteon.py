# -*- coding: utf-8 -*-
"""Test suite for Alteon Attribute Discovery """
from nose.tools import eq_

from rnms import model
from rnms.tests.att_discovery import AttDiscTest
from rnms.lib import states

from rnms.lib.att_discovers.alteon import discover_alteon_realservers, cb_alteon_realservers, discover_alteon_realservices, cb_alteon_realservices, discover_alteon_virtualservers, cb_alteon_virtualservers

class TestAlteonRealServer(AttDiscTest):
    values = [{'1': '1'}, {'1': '192.0.2.1'}, {'1': '12345'}, {'1': '2'}, {'1': 'realhost'}, {'1': '2'},]
    def test_none(self):
        """ Alteon RServer callback with None has no peers """
        self.check_callback_none(cb_alteon_realservers)

    def test_empty(self):
        """ Alteon RServer callback with empty dict has no peers """
        self.check_callback_empty(cb_alteon_realservers, 6)

    def test_single_rserver(self):
        """ Alteon Rserver finds one real server """
        values = self.get_values()
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
        values = self.get_values(1,{})
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(0)
    
    def test_missing_missing_admin(self):
        """ Alteon Rserver missing admin uses default up """
        values = self.get_values(3,{})
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_admin_state({'1': states.STATE_UP})
    
    def test_missing_missing_oper(self):
        """ Alteon Rserver missing oper uses default up """
        values = self.get_values(5,{})
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_oper_state({'1': states.STATE_UP})
    
    def test_single_admin_down_rserver(self):
        """ Alteon Rserver finds one real server admin down """
        values = self.get_values(3,{'1':'1'})
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_oper_state({'1': states.STATE_UP})
        self.assert_admin_state({'1': states.STATE_DOWN})
    
    def test_single_oper_down_rserver(self):
        """ Alteon Rserver finds one real server oper down """
        values = self.get_values(5, {'1': '1'})
        cb_alteon_realservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_oper_state({'1': states.STATE_DOWN})
        self.assert_admin_state({'1': states.STATE_UP})

    def test_discover_alteon_rserver(self):
        """ Alteon Real Server calls snmp correctly """
        eq_(discover_alteon_realservers(self.test_host, **self.discover_kwargs), True)
        self.assert_snmp_table_called()



class TestAlteonRealService(AttDiscTest):
    values = [{'1': '1'}, {'1': '3'}, {'1': '192.0.2.1'}, {'1': '80'}, {'1': '2'}, {'1': '192.0.2.2'}, {'1': '2'}, {'1': 'example.net'}, {'1': 'www'}]
    def test_none(self):
        """ Alteon RService callback with None has no peers """
        self.check_callback_none(cb_alteon_realservices)

    def test_empty(self):
        """ Alteon RService callback with empty dict has no attributes """
        self.check_callback_empty(cb_alteon_realservices, 9)

    def test_single_rservice(self):
        """ Alteon Rservice finds one real service """
        values = self.get_values()
        cb_alteon_realservices(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_result_indexes(('1.3.192.0.2.1',))
        self.assert_result_display_names(('192.0.2.2:80',))
        self.assert_result_fields('ipaddress', {'1.3.192.0.2.1': '192.0.2.2'})
        self.assert_result_fields('port', {'1.3.192.0.2.1': '80'})
        self.assert_result_fields('real_server', {'1.3.192.0.2.1': '192.0.2.1'})
        self.assert_oper_state({'1.3.192.0.2.1': states.STATE_UP})
        self.assert_admin_state({'1.3.192.0.2.1': states.STATE_UP})
    
    def test_missing_serivce_idx(self):
        """ Alteon Rservice mising serviceindex skips entry """
        values = self.get_values(1, {})
        cb_alteon_realservices(values, None, **self.test_callback_kwargs)
        self.assert_result_count(0)
    
    def test_single_oper_down_rservice(self):
        """ Alteon Rservice finds one real server oper down """
        values = self.get_values(4, {'1': '1'})
        cb_alteon_realservices(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_oper_state({'1.3.192.0.2.1': states.STATE_DOWN})
        self.assert_admin_state({'1.3.192.0.2.1': states.STATE_UP})

    def test_single_admin_down_rservice(self):
        values = self.get_values(6, {'1': '1'})
        """ Alteon Rservice finds one real server admin down """
        cb_alteon_realservices(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_oper_state({'1.3.192.0.2.1': states.STATE_UP})
        self.assert_admin_state({'1.3.192.0.2.1': states.STATE_DOWN})

    def test_discover_alteon_rservice(self):
        """ Alteon Real Service calls snmp correctly """
        eq_(discover_alteon_realservices(self.test_host, **self.discover_kwargs), True)
        self.assert_snmp_table_called()


class TestAlteonVirtualServer(AttDiscTest):
    values = [{'1': '1'}, {'1': '192.0.2.1'}, {'1': '2'}, {'1': 'example.net'}, {'1': 'www'}, ]
    def test_none(self):
        """ Alteon VServer callback with None has no peers """
        self.check_callback_none(cb_alteon_virtualservers)

    def test_empty(self):
        """ Alteon VServer callback with empty dict has no attributes """
        self.check_callback_empty(cb_alteon_virtualservers, 9)

    def test_single_rserver(self):
        """ Alteon Rserver finds one virtual service """
        values = self.get_values()
        cb_alteon_virtualservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_result_indexes(('1',))
        self.assert_result_display_names(('192.0.2.1',))
        self.assert_result_fields('ipaddress', {'1': '192.0.2.1'})
        self.assert_result_fields('hostname', {'1': 'www.example.net'})
        self.assert_oper_state({'1': states.STATE_UP})
        self.assert_admin_state({'1': states.STATE_UP})
    
    def test_missing_dname(self):
        """ Alteon Rserver mising dname gives default name """
        values = self.get_values(3, {})
        cb_alteon_virtualservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_result_fields('hostname', {'1': 'unknown'})
    
    def test_missing_dname(self):
        """ Alteon Rserver mising serviceindex skips entry """
        values = self.get_values(4, {})
        cb_alteon_virtualservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_result_fields('hostname', {'1': 'unknown'})

    def test_missing_ipaddress(self):
        """ Alteon Rserver mising ipaddress skips entry """
        values = self.get_values(1, {})
        cb_alteon_virtualservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(0)

    def test_missing_oper(self):
        """ Alteon Rserver mising oper sets default up """
        values = self.get_values(4, {})
        cb_alteon_virtualservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_oper_state({'1': states.STATE_UP})
        self.assert_admin_state({'1': states.STATE_UP})

    def test_oper_down(self):
        """ Alteon Rserver finds one virtual server oper down """
        values = self.get_values(2, {'1': '1'})
        cb_alteon_virtualservers(values, None, **self.test_callback_kwargs)
        self.assert_result_count(1)
        self.assert_oper_state({'1': states.STATE_DOWN})
        self.assert_admin_state({'1': states.STATE_UP})

    def test_discover_alteon_rserver(self):
        """ Alteon Virtual Server calls snmp correctly """
        eq_(discover_alteon_virtualservers(self.test_host, **self.discover_kwargs), True)
        self.assert_snmp_table_called()
