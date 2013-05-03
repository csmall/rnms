# -*- coding: utf-8 -*-
"""Test suite for attribute discovery """
import types

import mock
from nose.tools import eq_

from rnms import model
from rnms.tests import setup_db, teardown_db

from rnms.lib.snmp.engine import SNMPRequest
from rnms.lib.tcpclient import TCPClient

# Create an empty database before we start our tests for this module
def setup():
    """Function called by nose on module load"""
    setup_db()

# Tear down that database
def teardown():
    """Function called by nose after all tests in this module ran"""
    teardown_db()


class AttDiscTest(object):
    """ Base test case for the Attribute Discovery """
    klass = None
    atts = {}
    test_host_id = 123
    test_host_ip = '127.0.0.2'

    def setUp(self):
        self.dobj = mock.MagicMock()
        self.disc_cb = mock.Mock()
        self.dobj.discover_callback = self.disc_cb
        self.snmp_engine = mock.MagicMock()
        self.snmp_engine.get_table = mock.Mock(return_value=True)
        self.snmp_engine.get = mock.Mock(return_value=True)
        self.dobj.snmp_engine = self.snmp_engine
        self.tcp_client = mock.MagicMock(spec_set=TCPClient)
        self.tcp_client.get_tcp = mock.Mock(return_value=True)
        self.dobj.tcp_client = self.tcp_client

        self.test_host = mock.MagicMock(spec=model.Host)
        self.test_host.id = self.test_host_id
        self.test_host.mgmt_address = self.test_host_ip
        self.test_att_type = mock.MagicMock(spec=model.AttributeType)
        self.test_att_type.id = 1
        self.test_att_type.ad_parameters = ''
        self.test_callback_kwargs = {
                'dobj': self.dobj,
                'host': self.test_host,
                'att_type': self.test_att_type,
                }
        self.discover_kwargs = {
                'dobj': self.dobj,
                'att_type': self.test_att_type,
                }

    def get_values(self, changes=None, cvalue=None):
        """
        Return a copy of the default set of values with updates
        """
        values = self.values[:]
        if changes is not None:
            if cvalue is not None:
                values[changes] = cvalue
            else:
                for k,v in changes:
                    values[k] = v
        return values

    def set_ad_parameters(self, params):
        """ Set the AttributeType autodiscovery parameters """
        self.test_att_type.ad_parameters = params

    def assert_callback(self, new_attributes):
        """ Check the discover callback was called """
        self.disc_cb.assert_called_once_with(self.test_host_id, new_attributes)

    def check_callback_none(self, cb_fun):
        """ Check discovery callback that has been returned None """
        cb_fun(None, None, **self.test_callback_kwargs)
        self.assert_callback({})

    def check_callback_empty(self, cb_fun, rows):
        """ Check discovery callback that has been returned empty rows """
        cb_fun(None, None, **self.test_callback_kwargs)
        self.assert_callback({})

    def assert_result_count(self, expected_count):
        """ Callback results should have the expected count """
        self.disc_cb.assert_call_count(1)
        eq_(len(self.disc_cb.call_args[0][1]), expected_count)

    def assert_result_indexes(self, expected_keys):
        """ Check that the indexes are what we expect """
        eq_(set(self.disc_cb.call_args[0][1].keys()), set(expected_keys))

    def assert_result_display_names(self, expected_names):
        """ Check that the display_names are what we expect """
        got_names = set([ x.display_name for x in self.disc_cb.call_args[0][1].values()])
        eq_(got_names, set(expected_names))

    def assert_result_fields(self, field_name, expected_fields):
        """ Check that this field is filled with the correct values
        field_name is the name of field, the values are a dictionary
        using the index as a key
        """
        for idx,exp_value in expected_fields.items():
            eq_(self.disc_cb.call_args[0][1][idx].get_field(field_name), exp_value)

    def assert_oper_state(self, expected_states):
        for idx,oper_state in expected_states.items():
            eq_(self.disc_cb.call_args[0][1][idx].oper_state, oper_state)

    def assert_admin_state(self, expected_states):
        for idx,admin_state in expected_states.items():
            eq_(self.disc_cb.call_args[0][1][idx].admin_state, admin_state)

    # Discovery checks
    def assert_snmp_table_called(self):
        eq_(self.snmp_engine.get_table.called, True)
        # First parameter is host
        eq_(self.snmp_engine.get_table.call_args[0][0], self.test_host)
        # Second parameter is oids
        eq_(type(self.snmp_engine.get_table.call_args[0][1]), tuple)
        # Third parameter is a callback function
        eq_(type(self.snmp_engine.get_table.call_args[0][2]), types.FunctionType)
    def assert_snmp_get_called(self, oid_count=None):
        """ Check that the snmp_engine.get() method called correctly
        oid_count is number of oids in the request
        """
        eq_(self.snmp_engine.get.called, True)
        req = self.snmp_engine.get.call_args[0][0]
        eq_(type(req), SNMPRequest)
        eq_(req.host, self.test_host)
        if oid_count is not None:
            eq_(len(req.oids), oid_count)


    def assert_get_tcp_called(self, port, sendstr, maxbytes, cb_fun):
        self.tcp_client.get_tcp.assert_called_once_with(self.test_host, port, sendstr, maxbytes, cb_fun, **self.discover_kwargs)

