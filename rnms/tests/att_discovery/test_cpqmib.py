# -*- coding: utf-8 -*-
"""Test suite for CPQ MIB discovery """

from nose.tools import assert_true, assert_false

from rnms.tests.att_discovery import AttDiscTest
from rnms.lib.att_discovers.cpqmib import discover_cpqmib,\
    cb_cpqmib_phydrv, cb_cpqmib_fans, cb_cpqmib_temp,\
    cb_cpqmib_ps


class TestCpqmib(AttDiscTest):
    __ad_parameters__ = 'phydrv'

    def test_disc_ok(self):
        """ Disc Cpq calls SNMP table """
        assert_true(discover_cpqmib(*self.discover_args))
        self.assert_snmp_table_called()

    def test_disc_bad_param(self):
        """ Disc Cpq with bad AD parameters """
        self.set_ad_parameters("notthis")
        assert_false(discover_cpqmib(*self.discover_args))

    def test_cb_phydrv_none(self):
        """ AdiscCB Cpq PhyDrv with none """
        self.check_callback_none(cb_cpqmib_phydrv)

    def test_cb_phydrv_twoup(self):
        """ AdiscCB Cpq PhyDrv with two objects """
        values = (('0', '1', '2', '2'), ('1', '2', '3', '2'))
        self.callback(cb_cpqmib_phydrv, values)
        self.assert_result_count(2)
        self.assert_result_indexes(('0.1', '1.2'))
        self.assert_oper_state({'0.1': 'up', '1.2': 'up'})

    def test_cb_phydrv_onedown(self):
        """ AdiscCB Cpq PhyDrv with one down """
        values = (('0', '1', '2', '3'), ('1', '2', '3', '2'))
        self.callback(cb_cpqmib_phydrv, values)
        self.assert_result_count(2)
        self.assert_result_indexes(('0.1', '1.2'))
        self.assert_oper_state({'0.1': 'down', '1.2': 'up'})

    def test_cb_fans_none(self):
        """ AdiscCB Cpq fans with none """
        self.check_callback_none(cb_cpqmib_fans)

    def test_cb_fans_twoup(self):
        """ AdiscCB Cpq fans with two objects """
        values = (('0', '1', '2', '2', '2'), ('1', '2', '3', '2', '2'))
        self.callback(cb_cpqmib_fans, values)
        self.assert_result_count(2)
        self.assert_result_indexes(('0.1', '1.2'))
        self.assert_oper_state({'0.1': 'up', '1.2': 'up'})

    def test_cb_fans_onedown(self):
        """ AdiscCB Cpq fans with one down """
        values = (('0', '1', '2', '2', '3'), ('1', '2', '3', '2', '2'))
        self.callback(cb_cpqmib_fans, values)
        self.assert_result_count(2)
        self.assert_result_indexes(('0.1', '1.2'))
        self.assert_oper_state({'0.1': 'down', '1.2': 'up'})

    def test_cb_temp_none(self):
        """ AdiscCB Cpq temp with none """
        self.check_callback_none(cb_cpqmib_temp)

    def test_cb_temp_twoup(self):
        """ AdiscCB Cpq temp with two objects """
        values = (('0', '1', '2', '2'), ('1', '2', '3', '2'))
        self.callback(cb_cpqmib_temp, values)
        self.assert_result_count(2)
        self.assert_result_indexes(('0.1', '1.2'))
        self.assert_oper_state({'0.1': 'up', '1.2': 'up'})

    def test_cb_temp_onedown(self):
        """ AdiscCB Cpq temp with one down """
        values = (('0', '1', '2', '3'), ('1', '2', '3', '2'))
        self.callback(cb_cpqmib_temp, values)
        self.assert_result_count(2)
        self.assert_result_indexes(('0.1', '1.2'))
        self.assert_oper_state({'0.1': 'down', '1.2': 'up'})

    def test_cb_ps_none(self):
        """ AdiscCB Cpq ps with none """
        self.check_callback_none(cb_cpqmib_ps)

    def test_cb_ps_twoup(self):
        """ AdiscCB Cpq ps with two objects """
        values = (('0', '1', '2', '2', '2'), ('1', '2', '3', '2', '2'))
        self.callback(cb_cpqmib_ps, values)
        self.assert_result_count(2)
        self.assert_result_indexes(('0.1', '1.2'))
        self.assert_oper_state({'0.1': 'up', '1.2': 'up'})

    def test_cb_ps_onedown(self):
        """ AdiscCB Cpq ps with one down """
        values = (('0', '1', '2', '2', '3'), ('1', '2', '3', '2', '2'))
        self.callback(cb_cpqmib_ps, values)
        self.assert_result_count(2)
        self.assert_result_indexes(('0.1', '1.2'))
        self.assert_oper_state({'0.1': 'down', '1.2': 'up'})
