# -*- coding: utf-8 -*-
"""Test suite for Cisco SNMP discovery """

from rnms.tests.att_discovery import AttDiscTest

from rnms.lib.att_discovers.cisco_snmp import \
        discover_cisco_envmib, cb_cisco_envmib,\
        discover_cisco_saagent, cb_cisco_saagent,\
        discover_pix_connections, cb_pix_connections


class TestCiscoEnvmib(AttDiscTest):
    
    def setUp(self):
        super(TestCiscoEnvmib, self).setUp()
        self.test_att_type.ad_parameters='namebase,1,2'
        self.test_callback_kwargs['name_base'] = 'namebase'

    def test_cb_none(self):
        """ Cisco Env disc callback with None has no attributes """
        self.check_callback_none(cb_cisco_envmib)
    
    def test_cb_empty(self):
        """ Cisco Env disc callback with empty dict has no attributes """
        self.check_callback_empty(cb_cisco_envmib, 2)

    def test_cb_single(self):
        """ Cisco Env disc callback finds single peer """
        values = [{'1': 'testdev'}, {'1': '1'}]
        self.callback(cb_cisco_envmib, values)
        self.assert_result_count(1)
        self.assert_oper_state({'1': 'normal'})
        self.assert_admin_state({'1': 'up'})
    
    def test_cb_oper_warning(self):
        """ Cisco Env disc callback finds single oper warning peer """
        values = [{'1': 'testdev'}, {'1': '2'}]
        self.callback(cb_cisco_envmib, values)
        self.assert_result_count(1)
        self.assert_oper_state({'1': 'warning'})
        self.assert_admin_state({'1': 'up'})
    
    def test_cb_admin_down(self):
        """ Cisco Env disc callback finds single admin down peer """
        values = [{'1': 'testdev'}, {'1': '5'}]
        self.callback(cb_cisco_envmib, values)
        self.assert_result_count(1)
        self.assert_oper_state({'1': 'not present'})
        self.assert_admin_state({'1': 'down'})

    def test_discover(self):
        """ Cisco Env disc calls snmp table correctly """
        self.discover(discover_cisco_envmib)
        self.assert_snmp_table_called()
        
class TestCiscoSAAgent(AttDiscTest):
    
    def test_cb_none(self):
        """ Cisco SAAgent disc callback with None has no attributes """
        self.check_callback_none(cb_cisco_saagent)
    
    def test_cb_empty(self):
        """ Cisco SAAgent disc callback with empty dict has no attributes """
        self.check_callback_empty(cb_cisco_saagent, 2)

    def test_cb_single(self):
        """ Cisco SAAgent disc callback finds single peer """
        values = [{'1': '2'}, {'1': 'test'}]
        self.callback(cb_cisco_saagent, values)
        self.assert_result_count(1)
        self.assert_oper_state({'1': 'up'})
        self.assert_admin_state({'1': 'up'})
        self.assert_result_display_names(('SAA1 test',))
    
    def test_discover(self):
        """ Cisco SAAgent disc calls snmp table correctly """
        self.discover(discover_cisco_saagent)
        self.assert_snmp_table_called()
        
class TestCiscoPIX(AttDiscTest):
    
    def test_cb_none(self):
        """ Cisco PIX disc callback with None has no attributes """
        self.check_callback_none(cb_pix_connections)
    
    def test_cb_empty(self):
        """ Cisco PIX disc callback with empty dict has no attributes """
        self.check_callback_empty(cb_pix_connections, 2)

    def test_cb_single(self):
        """ Cisco PIX disc callback finds single peer """
        values = [{'1': '2'}, {'1': 'test'}]
        self.callback(cb_pix_connections, values)
        self.assert_result_count(1)
        self.assert_oper_state({'1': 'up'})
        self.assert_admin_state({'1': 'up'})
        self.assert_result_display_names(('FW Stat1',))
    
    def test_discover(self):
        """ Cisco PIX disc calls snmp table correctly """
        self.discover(discover_pix_connections)
        self.assert_snmp_table_called()
        
