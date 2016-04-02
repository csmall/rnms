# -*- coding: utf-8 -*-
"""Test suite for SNMP FC ports Attribute Discovery """
from nose.tools import assert_true
from rnms.tests.att_discovery import AttDiscTest
from rnms.lib.discovery.plugins.attributes.snmp_fcport import\
    discover_fc_ports, cb_fc_ports


class TestSnmpFc(AttDiscTest):
    def test_disc_ok(self):
        """ Disc fc port calls SNMP get_table """
        assert_true(discover_fc_ports(*self.discover_args))
        self.assert_snmp_table_called()

    def test_none(self):
        """ CbDisc fc port with none """
        self.check_callback_none(cb_fc_ports)

    def test_cb_ok(self):
        """ CbDisc fc port with valid values """
        values = (
            (('1', '1'), ('1', '3')),
            (('2', '2'), ('2', '2')),
            (('3', '3'), ('3', '1')),
            )
        self.callback(cb_fc_ports, values)
        self.assert_result_count(3)
        self.assert_oper_state({'1': 'testing', '2': 'down', '3': 'up'})
