# -*- coding: utf-8 -*-
"""Test suite for attribute polling """
import types

import mock
from nose.tools import eq_

from rnms import model
from rnms.lib.snmp.engine import SNMPRequest, SNMPEngine
from rnms.lib.poller import Poller
from rnms.lib import states

class PollerTest(object):
    """ Base test class for Pollers """
    klass = None
    atts = {}
    test_host_id = 123
    test_host_ip = '127.0.0.2'
    test_attribute_id = 456
    test_default_value = 789
    #test_attribute_fields = None
    use_tcpclient = False

    def setUp(self):
        self.pobj = mock.MagicMock(spec_set=Poller)
        self.poller_cb = mock.Mock()
        self.pobj.poller_callback = self.poller_cb
        self.poller_buffer = {}
        self.pobj.poller_buffer = self.poller_buffer

        self.snmp_engine = mock.MagicMock(spec_set=SNMPEngine)
        self.snmp_engine.get_table = mock.Mock(return_value=True)
        self.snmp_engine.get = mock.Mock(return_value=True)
        self.snmp_engine.set = mock.Mock(return_value=True)
        self.snmp_engine.get_int = mock.Mock(return_value=True)
        self.snmp_engine.get_str = mock.Mock(return_value=True)
        self.snmp_engine.set = mock.Mock(return_value=True)
        self.pobj.snmp_engine = self.snmp_engine

        self.test_host = mock.MagicMock(spec_set=model.Host, name='testhost')
        self.test_host.id = self.test_host_id
        self.test_host.mgmt_address = self.test_host_ip
        self.test_host.community_ro = ('2', 'public')
        self.test_att_type = mock.MagicMock(spec_set=model.AttributeType)
        self.test_att_type.id = 1

        self.test_attribute = mock.MagicMock(spec_set=model.Attribute)
        self.test_attribute.id = self.test_attribute_id
        self.test_attribute.host_id = self.test_host_id
        self.test_attribute.host = self.test_host
        self.test_attribute.attribute_type.id = 1
        self.test_attribute.attribute_type = self.test_att_type
        
        self.test_poller_row = mock.MagicMock(spec=model.PollerRow)

        self.test_kwargs = {
                'pobj': self.pobj,
                'attribute': self.test_attribute,
                'poller_row': self.test_poller_row,
                'default_value': self.test_default_value,
                }

        if self.use_tcpclient == True:
            self._setup_tcpclient()

    def _setup_tcpclient(self):
        from rnms.lib.tcpclient import TCPClient

        self.tcp_client = mock.MagicMock(spec_set=TCPClient)
        self.tcp_client.get_tcp = mock.Mock(return_value=True)
        self.pobj.tcp_client = self.tcp_client
    
    def set_attribute_fields(self, fields):
        self.test_attribute_fields = fields
        self.test_attribute.get_fields = mock.Mock(return_value=self.test_attribute_fields)

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

    def assert_callback(self, values):
        """ Check the poller_callback was called """
        self.poller_cb.assert_called_once_with(self.test_attribute_id, self.test_poller_row, values)

    def assert_callback_default(self):
        self.poller_cb.assert_called_once_with(self.test_attribute_id, self.test_poller_row, self.test_default_value)
    
    def assert_callback_none(self, cb_fun):
        """ Poller with None returned should callback with default value """
        cb_fun(None, None, **self.test_kwargs)
        self.assert_callback(self.test_default_value)
    
    def assert_callback_none_none(self, cb_fun):
        """ Poller with None returned should callback with none """
        cb_fun(None, None, **self.test_kwargs)
        self.assert_callback(None)
    
    def assert_callback_empty(self, cb_fun):
        """ Poller with empty list returned should callback with default value """
        cb_fun([], None, **self.test_kwargs)
        self.assert_callback(self.test_default_value)

    def assert_callback_empty_dict(self, cb_fun):
        """ Poller with empty dict returned should callback with default value """
        cb_fun({}, None, **self.test_kwargs)
        self.assert_callback(self.test_default_value)

    def assert_callback_value(self, cb_fun, cb_value, expected_value):
        cb_fun(cb_value, None, **self.test_kwargs)
        self.assert_callback(expected_value)

    def assert_get_int_called(self, cb_func, extra_kwargs=None, oid=(1,2,3)):
        if extra_kwargs is not  None:
            self.test_kwargs.update(extra_kwargs)
        self.snmp_engine.get_int.assert_called_once_with(self.test_host,oid, cb_func, **self.test_kwargs)

    def assert_get_str_called(self, oid, cb_func, extra_kwargs=None):
        if extra_kwargs is not  None:
            self.test_kwargs.update(extra_kwargs)
        self.snmp_engine.get_str.assert_called_once_with(self.test_host,oid, cb_func, **self.test_kwargs)

    def assert_get_table_called(self, cb_func, extra_kwargs=None):
        if extra_kwargs is not None:
            self.test_kwargs.update(extra_kwargs)
        self.snmp_engine.get_table.assert_called_once_with(self.test_host,'1.2.3', cb_func, table_trim=1, **self.test_kwargs)

    def assert_snmp_set_called(self, oid, cb_func, value, extra_kwargs=None):
        if extra_kwargs is not  None:
            self.test_kwargs.update(extra_kwargs)
        self.snmp_engine.set.assert_called_once()
        called_vars = self.snmp_engine.set.call_args[0]
        eq_(type(called_vars[0]), SNMPRequest)
        eq_(called_vars[0].oids[0]['oid'], oid)
        eq_(called_vars[0].oids[0]['callback'], cb_func)
        eq_(called_vars[0].oids[0]['value'], value)
        #_with(self.test_host,oid, cb_func, **self.test_kwargs)


    def assert_tcp_client_called(self, port, send_str, max_bytes, cb_fun):
        assert(self.use_tcpclient)
        self.tcp_client.get_tcp.assert_called_once_with(self.test_host, port, send_str, max_bytes, cb_fun, **self.test_kwargs)


