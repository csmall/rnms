# -*- coding: utf-8 -*-
"""Test suite for sensors discovery """

from nose.tools import assert_true

from rnms.tests.att_discovery import AttDiscTest
from rnms.lib.att_discovers.sensors import discover_sensors,\
    cb_sensors


class TestSesnors(AttDiscTest):

    def test_disc_ok(self):
        """ Disc sensors calls SNMP many """
        assert_true(discover_sensors(*self.discover_args))
        self.assert_snmp_many_called()

    def test_cb_none(self):
        """ Disc Sensors with None """
        self.check_callback_none(cb_sensors)

    def test_cb_ok(self):
        """ CbDisc Sensors with valid values """
        values = (
            (('2.1.2.1', 'temp1'), ('2.1.2.16', 'temp2'),
                ('2.1.2.16', 'temp2'),),
            (('3.1.2.11', 'fan1'), ('3.1.2.12', 'fan2'),
                ('3.1.2.13', 'fan3'), ('3.1.2.14', 'fan4')),
            (('4.1.2.2', 'in0'), ('4.1.2.3', 'in1'), ('4.1.2.4', 'in2'),),
            [])
        self.callback(cb_sensors, values)
        self.assert_result_count(9)
        self.assert_result_display_names(
            ('temp1', 'temp2', 'fan1', 'fan2', 'fan3', 'fan4', 'in0',
                'in1', 'in2'))
        self.assert_result_indexes(
            ('4.4', '4.3', '4.2', '3.11', '3.12', '3.13', '3.14', '2.16',
                '2.1'))
        self.assert_result_fields(
            'units', {'4.4': 'V', '4.3': 'V', '4.2': 'V',
                      '3.11': 'RPM', '3.12': 'RPM', '3.13': 'RPM',
                      '3.14': 'RPM', '2.16': 'degC', '2.1': 'degC'})
