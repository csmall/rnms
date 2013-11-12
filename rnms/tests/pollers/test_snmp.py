# -*- coding: utf-8 -*-
"""Test suite for SNMP Pollers """
from nose.tools import eq_

from rnms import model
from rnms.tests.pollers import PollerTest
from rnms.lib import states

from rnms.lib.pollers.snmp import poll_snmp_counter, cb_snmp_counter, poll_snmp_status, cb_snmp_status, poll_snmp_walk_average, cb_snmp_walk_average, poll_snmp_counter_mul

class TestSnmpPoller(PollerTest):

    def test_counter_poll_empty(self):
        """ snmp_counter with no params returns false """
        eq_(poll_snmp_counter(self.poller_buffer, '', **self.test_kwargs), False)
    def test_counter_poll_badparam(self):
        """ snmp_counter with bad params returns false """
        eq_(poll_snmp_counter(self.poller_buffer, 'fooo', **self.test_kwargs), False)

    def test_counter_poll(self):
        """ snmp_counter works """
        eq_(poll_snmp_counter(self.poller_buffer, '1.2.3', **self.test_kwargs), True)
        self.assert_get_int_called(cb_snmp_counter, {})

    def test_counter_poll_mul_empty(self):
        """ snmp_counter_mul with no params returns false """
        eq_(poll_snmp_counter_mul(self.poller_buffer, '', **self.test_kwargs), False)
    def test_counter_poll_mul_badparam(self):
        """ snmp_counter_mul with bad params returns false """
        eq_(poll_snmp_counter_mul(self.poller_buffer, 'fooo', **self.test_kwargs), False)

    def test_counter_poll_mul(self):
        """ poll_snmp_counter_mull works """
        eq_(poll_snmp_counter_mul(self.poller_buffer, '1.2.3|10', **self.test_kwargs), True)
        self.assert_get_int_called(cb_snmp_counter, {'multiplier':10})

    def test_counter_none(self):
        """ cb_snmp_counter with None """
        self.assert_callback_none(cb_snmp_counter)

    def test_counter_value(self):
        """ cb_snmp_counter with value """
        self.assert_callback_value(cb_snmp_counter, '42', '42')

    def test_counter_mul(self):
        """ cb_snmp_counter with multipler """
        cb_snmp_counter('100', None, multiplier=8, **self.test_kwargs)
        self.assert_callback(800)
    
    def test_counter_div(self):
        """ cb_snmp_counter with divider gives calced result """
        cb_snmp_counter('100', None, multiplier=0.1, **self.test_kwargs)
        self.assert_callback(10)

    ### snmp_status
    def test_status_poll_empty(self):
        """ snmp_status with no params returns false """
        eq_(poll_snmp_status(self.poller_buffer, '', **self.test_kwargs), False)
    def test_status_poll_badparam(self):
        """ snmp_status with bad params returns false """
        eq_(poll_snmp_status(self.poller_buffer, 'fooo', **self.test_kwargs), False)
    def test_status_poll_badoid(self):
        """ snmp_status with bad oid returns false """
        eq_(poll_snmp_status(self.poller_buffer, 'badoid|1=2', **self.test_kwargs), False)

    def test_status_poll_full(self):
        """ poll_snmp_status with mapping and default return true """
        eq_(poll_snmp_status(self.poller_buffer, '1.2.3|1=2|3', **self.test_kwargs), True)
        self.assert_get_str_called((1,2,3), cb_snmp_status, {'mapping':'1=2',
            'default_state': '3'})
    
    def test_status_poll_no_default(self):
        """ poll_snmp_status with mapping return true """
        eq_(poll_snmp_status(self.poller_buffer, '1.2.3|1=2', **self.test_kwargs), True)
        self.assert_get_str_called((1,2,3), cb_snmp_status, {'mapping':'1=2',
            'default_state': None})

    def test_status_poll_no_mapping(self):
        """ poll_snmp_status with no mapping return False """
        eq_(poll_snmp_status(self.poller_buffer, '1.2.3', **self.test_kwargs), False)

    def test_status_none(self):
        """ cb_snmp_status with None returns default """
        cb_snmp_status(None, None, default_state=None, **self.test_kwargs)
        self.assert_callback_default()

    def test_status_no_mapping(self):
        """ cb_snmp_status with no mapping gives None """
        cb_snmp_status('100', None, default_state=None, **self.test_kwargs)
        self.assert_callback_default()

    def test_status_bad_mapping(self):
        """ cb_snmp_status with bad mapping returns None """
        cb_snmp_status('100', None, mapping='foo', default_state=None,
                       **self.test_kwargs)
        self.assert_callback_default()

    def test_status_bad_mapping_miss(self):
        """ cb_snmp_status with bad mapping on missed item returns
        correctly """
        cb_snmp_status('100', None, mapping='foo,100=up', default_state=None,
                       **self.test_kwargs)
        self.assert_callback('up')

    def test_status_miss_mapping(self):
        """ cb_snmp_status with no match on mapping returns None """
        cb_snmp_status('100', None, mapping='1=up,2=do', default_state=None,
                       **self.test_kwargs)
        self.assert_callback_default()

    def test_status_mapping(self):
        """ cb_snmp_status with match returns result """
        cb_snmp_status('2', None, mapping='1=up,2=do', default_state=None,
                       **self.test_kwargs)
        self.assert_callback('do')

    # snmp_alk_average
    def test_walkavg_poll_empty(self):
        """ poll_snmp_walk_average with no params returns false """
        eq_(poll_snmp_walk_average(self.poller_buffer, '', **self.test_kwargs), False)

    def test_walkavg_poll(self):
        """ poll_snmp_walk_average """
        eq_(poll_snmp_walk_average(self.poller_buffer, '1.2.3', **self.test_kwargs), True)
        self.assert_get_table_called(cb_snmp_walk_average,
                                     extra_kwargs={'with_oid':1})

    def test_walkavg_none(self):
        """ cb_snmp_walk_average with None returns default """
        self.assert_callback_none(cb_snmp_walk_average)
    
    def test_walkavg_empty(self):
        """ cb_snmp_walk_average with empty returns default """
        self.assert_callback_empty_dict(cb_snmp_walk_average)
    
    def test_walkavg_onebad(self):
        """ cb_snmp_walk_average with one bad result ignores that result """
        cb_snmp_walk_average({'1': '10','2':'foo', '3': '20'}, None, **self.test_kwargs)
        self.assert_callback((10+20)/2)

    def test_walkavg_allbad(self):
        """ cb_snmp_walk_average with all bad results returns default """
        cb_snmp_walk_average({'1': 'foo','2':'bar', '3': 'bazz'}, None, **self.test_kwargs)
        self.assert_callback_default()
    
    def test_walkavg_good(self):
        """ cb_snmp_walk_average with good result """
        cb_snmp_walk_average({str(x):str(x) for x in range(1,5)}, None, **self.test_kwargs)
        self.assert_callback(2.5)
