# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.

This is an example of how functional tests can be written for controllers.

As opposed to a unit-test, which test a small unit of functionality,
functional tests exercise the whole application and its WSGI stack.

Please read http://pythonpaste.org/webtest/ for more information.

"""
from nose.tools import eq_
import mock

from rnms.lib.snmp import SNMPEngine
from rnms.lib import zmqcore
from rnms.model import Host, SnmpCommunity


def my_callback1(value, error, **kwargs):
    if 'obj' not in kwargs:
        assert False
        return
    kwargs['obj'].results.append(value)


class NoTestSNMP(object):
    """ Base unit for SNMP testing """
    sysobjid_oid = (1, 3, 6, 1, 2, 1, 1, 2, 0)
    expected_sysobjid = "1.3.6.1.4.1.8072.3.2.10"

    def setUp(self):
        """ Setup the SNMP engine """
        self.zmq_core = zmqcore.ZmqCore()
        self.snmp_engine = SNMPEngine(self.zmq_core, mock.Mock())
        self.results = []
        self.test_host = mock.MagicMock(spec_set=Host)
        self.test_host.ro_community = mock.MagicMock(spec_set=SnmpCommunity)
        self.test_host.mgmt_address = '127.0.0.1'

    def set_host(self, snmpver, snmpcomm):
        self.test_host.ro_community.community = snmpcomm
        self.test_host.ro_community.version = snmpver
        self.test_host.ro_community.is_snmpv1 = mock.Mock(
            return_value=(snmpver == 1))
        self.test_host.ro_community.is_snmpv2 = mock.Mock(
            return_value=(snmpver == 2))

    def poll(self):
        while (self.snmp_engine.poll() > 0):
            self.zmq_core.poll(0.1)

    def test_valid_timeout(self):
        """ Valid timeout value updates default SNMP timeout """
        self.snmp_engine.set_default_timeout("123")
        eq_(self.snmp_engine.default_timeout, 123)

    def test_bad_timeout(self):
        """ Invalid timeout value doesnt change timeout """
        default_timeout = self.snmp_engine.default_timeout
        self.snmp_engine.set_default_timeout("Not a number")
        eq_(self.snmp_engine.default_timeout, default_timeout)

    def test_v1get(self):
        """ Simple SNMP v1 fetch of SysObjectID """
        self.set_host(1, 'public')
        assert(self.snmp_engine.get_str(
            self.test_host, self.sysobjid_oid, my_callback1, obj=self))
        self.poll()
        eq_(self.results, [self.expected_sysobjid, ])

    def test_v2get(self):
        """ Simple SNMP v2 fetch of SysObjectID """
        self.set_host(2, 'public')
        self.snmp_engine.get_str(
            self.test_host, self.sysobjid_oid, my_callback1, obj=self)
        self.poll()
        eq_(self.results, [self.expected_sysobjid, ])

    def test_v1_default_bad_comm(self):
        """ Simple SNMP v1 fetch returns default with bad community"""
        self.set_host(1, 'badcomm')
        self.snmp_engine.set_default_timeout(1)
        self.snmp_engine.get_str(
            self.test_host, self.sysobjid_oid, my_callback1,
            default="42", obj=self)
        self.poll()
        eq_(self.results, ["42"])

    def test_v2_default_bad_comm(self):
        """ Simple SNMP v2c fetch returns default with bad community"""
        self.set_host(2, 'badcomm')
        self.snmp_engine.set_default_timeout(1)
        self.snmp_engine.get_str(
            self.test_host, self.sysobjid_oid, my_callback1,
            default="42", obj=self)
        self.poll()
        eq_(self.results, ["42"])

    def test_v1_default_bad_oid(self):
        """ Simple SNMP v1 fetch returns default with bad OID"""
        self.set_host(1, 'public')
        self.snmp_engine.set_default_timeout(1)
        self.snmp_engine.get_str(
            self.test_host, '1.3.6.42.41.40', my_callback1,
            default="42", obj=self)
        self.poll()
        eq_(self.results, ["42"])

    def test_v2_default_bad_oid(self):
        """ Simple SNMP v2c fetch returns default with bad OID"""
        self.set_host(2, 'public')
        self.snmp_engine.set_default_timeout(1)
        self.snmp_engine.get_str(
            self.test_host, '1.3.6.42.41.40', my_callback1,
            default="42", obj=self)
        self.poll()
        eq_(self.results, ["42"])

    def test_v1_table(self):
        """ SNMP v1 table fetch - uses ifTable.ifIndex """
        self.set_host(1, 'public')
        self.snmp_engine.set_default_timeout(1)
        # Get size of iftable
        self.snmp_engine.get_int(
            self.test_host, '1.3.6.1.2.1.2.1.0', my_callback1, obj=self)
        self.poll()
        eq_(len(self.results), 1)
        table_length = self.results[0]

        self.snmp_engine.get_table(
            self.test_host, ('1.3.6.1.2.1.2.2.1.1',), my_callback1,
            table_trim=1, obj=self)
        self.poll()
        eq_(len(self.results),2)
        eq_(len(self.results[1][0]),table_length)
        for oid,val in self.results[1][0].items():
            assert(oid == val)

    def test_v2_table(self):
        """ SNMP v2 table fetch - uses ifTable.ifIndex """
        self.set_host(2, 'public')
        # Get size of iftable
        self.snmp_engine.get_int(
            self.test_host, '1.3.6.1.2.1.2.1.0', my_callback1, obj=self)
        self.poll()
        eq_(len(self.results),1)
        table_length = self.results[0]

        self.snmp_engine.get_table(
            self.test_host, '1.3.6.1.2.1.2.2.1.1', my_callback1, table_trim=1, obj=self )
        self.poll()
        eq_(len(self.results),2)
        eq_(len(self.results[1][0]),table_length)
        for oid,val in self.results[1][0].items():
            assert(oid == val)
