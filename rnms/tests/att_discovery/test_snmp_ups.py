# -*- coding: utf-8 -*-
"""Test suite for SNMP UPS discovery """

from nose.tools import assert_true, assert_false

from rnms.tests.att_discovery import AttDiscTest
from rnms.lib.discovery.plugins.attributes.snmp_ups\
    import discover_ups, cb_ups, discover_ups_lines, cb_ups_lines


class TestUps(AttDiscTest):

    def test_disc_ups_ok(self):
        """ Disc UPS calls get_list correctly """
        assert_true(discover_ups(*self.discover_args))
        self.assert_snmp_list_called()

    def test_cb_ups_none(self):
        """ CbDisc UPS with None """
        self.check_callback_none(cb_ups)

    def test_cb_ups_empty(self):
        """ CbDisc UPS with no values """
        self.check_callback_empty_list(cb_ups, 4)

    def test_cb_ups_normal(self):
        """ CbDisc UPS with standard UPS """
        values = ('42', 'name', None, None)
        self.callback(cb_ups, values)
        self.assert_result_count(1)
        self.assert_result_indexes('1')
        self.assert_result_fields('ups_oid', {'1': '1.3.6.1.2.1.33.1'})

    def test_cb_ups_mit(self):
        """ CbDisc UPS with mit UPS """
        values = (None, None, '42', 'name')
        self.callback(cb_ups, values)
        self.assert_result_count(1)
        self.assert_result_indexes('1')
        self.assert_result_fields('ups_oid', {'1': '1.3.6.1.4.1.13891.101'})

    def test_disc_upsline_ok(self):
        """ Disc UPS lines calls get_table """
        self.set_ad_parameters('1.2.3|in|0')
        assert_true(discover_ups_lines(*self.discover_args))

    def test_disc_upslines_badparms(self):
        """ Disc UPS lines with bad parameters """
        self.set_ad_parameters('12.3')
        assert_false(discover_ups_lines(*self.discover_args))

    def test_disc_upslines_badoid(self):
        """ Disc UPS lines with bad OID in params """
        self.set_ad_parameters('foo|in|0')
        assert_false(discover_ups_lines(*self.discover_args))

    def test_cb_upslines_none(self):
        """ CbDisc UPS lines with none """
        self.check_callback_none(cb_ups_lines)

    def NOtest_cb_upslines_ok(self):
        """ CbDisc UPS lines with valid data """
        values = (('1', ), ('2',), ('3',))
        self.callback(cb_ups_lines, values)
        self.assert_result_count(3)
