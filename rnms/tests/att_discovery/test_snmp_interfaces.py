# -*- coding: utf-8 -*-
"""Test suite for SNMP Interfaces Attribute Discovery """
from nose.tools import assert_true

from rnms.tests.att_discovery import AttDiscTest

from rnms.lib.discovery.plugins.attributes.snmp import \
    discover_snmp_interfaces, cb_snmp_interfaces


class TestSNMPInts(AttDiscTest):
    def test_discover_(self):
        """ Disc snmp ints calls SNMP get many """
        self.set_ad_parameters('1.2.3|Item')
        assert_true(discover_snmp_interfaces(*self.discover_args))

    def test_cb_none(self):
        """ CbDisc snmp interfaces with None """
        self.check_callback_none(cb_snmp_interfaces)

    def test_cb_ok(self):
        """ CbDisc snmp interfaces with values """
        values = [
            [('1', 'lo'), ('2', 'eth0'), ('3', 'eth1'), ('4', 'virbr0')],
            [('1', '10000000'), ('2', '10000000'), ('3', '100000000'),
             ('4', '0')],
            [('1', '1'), ('2', '1'), ('3', '1'), ('4', '1')],
            [('1', '1'), ('2', '2'), ('3', '1'), ('4', '2')],
            [('1', '127.0.0.1'), ('1', '172.16.1.1'),
                ('1', '192.168.222.111')],
            [('1', '1'), ('1', '3'), ('1', '4')],
            [('1', '255.0.0.0'), ('1', '255.255.255.0'),
                ('1', '255.255.255.0')]]
        self.callback(cb_snmp_interfaces, values)
        self.assert_result_count(4)
        self.assert_result_indexes(('1', '2', '3', '4'))
        self.assert_result_display_names(('lo', 'eth0', 'eth1', 'virbr0'))
