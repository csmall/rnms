# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.

This is an example of how functional tests can be written for controllers.

As opposed to a unit-test, which test a small unit of functionality,
functional tests exercise the whole application and its WSGI stack.

Please read http://pythonpaste.org/webtest/ for more information.

"""
from nose.tools import assert_true, nottest, eq_

from rnms.lib.snmp import SNMPEngine
class DummyHost(object):
    mgmt_address = ''
    community_ro = {}
    def __init__(self, ip, snmpver, snmpcomm):
        self.mgmt_address = ip
        self.community_ro[0] = snmpver
        self.community_ro[1] = snmpcomm

def my_callback1(value, error, **kwargs):
    if 'obj' not in kwargs:
        assert False
        return
    kwargs['obj'].results.append(value)

class TestSNMP(object):
    """ Base unit for SNMP testing """
    sysobjid_oid = (1,3,6,1,2,1,1,2,0)
    expected_sysobjid = "1.3.6.1.4.1.8072.3.2.10"

    def setUp(self):
        """ Setup the SNMP engine """
        self.snmp_engine = SNMPEngine()
        self.results = []

    def poll(self):
        while (self.snmp_engine.poll()):
            pass

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
        host = DummyHost("127.0.0.1", 1, "public")
        assert(self.snmp_engine.get_str(host, self.sysobjid_oid, my_callback1, obj=self ))
        self.poll()
        eq_(self.results, [self.expected_sysobjid,])

    def test_v2get(self):
        """ Simple SNMP v2 fetch of SysObjectID """
        host = DummyHost("127.0.0.1", 2, "public")
        self.snmp_engine.get_str(host, self.sysobjid_oid, my_callback1, obj=self )
        self.poll()
        eq_(self.results, [self.expected_sysobjid,])

    def test_v1_default_bad_comm(self):
        """ Simple SNMP v1 fetch returns default with bad community"""
        host = DummyHost("127.0.0.1", 1, "badcomm")
        self.snmp_engine.set_default_timeout(1)
        self.snmp_engine.get_str(host, self.sysobjid_oid, my_callback1, default="42", obj=self )
        self.poll()
        eq_(self.results, ["42"])

    def test_v2_default_bad_comm(self):
        """ Simple SNMP v2c fetch returns default with bad community"""
        host = DummyHost("127.0.0.1", 2, "badcomm")
        self.snmp_engine.set_default_timeout(1)
        self.snmp_engine.get_str(host, self.sysobjid_oid, my_callback1, default="42", obj=self )
        self.poll()
        eq_(self.results, ["42"])

    def test_v1_default_bad_oid(self):
        """ Simple SNMP v1 fetch returns default with bad OID"""
        host = DummyHost("127.0.0.1", 1, "public")
        self.snmp_engine.set_default_timeout(1)
        self.snmp_engine.get_str(host, '1.3.6.42.41.40', my_callback1, default="42", obj=self )
        self.poll()
        eq_(self.results, ["42"])

    def test_v2_default_bad_oid(self):
        """ Simple SNMP v2c fetch returns default with bad OID"""
        host = DummyHost("127.0.0.1", 2, "public")
        self.snmp_engine.set_default_timeout(1)
        self.snmp_engine.get_str(host, '1.3.6.42.41.40', my_callback1, default="42", obj=self )
        self.poll()
        eq_(self.results, ["42"])

    def test_v1_table(self):
        """ SNMP v1 table fetch - uses ifTable.ifIndex """
        host = DummyHost("127.0.0.1", 1, "public")
        self.snmp_engine.set_default_timeout(1)
        # Get size of iftable
        self.snmp_engine.get_int(host, '1.3.6.1.2.1.2.1.0', my_callback1, obj=self)
        self.poll()
        eq_(len(self.results),1)
        table_length = self.results[0]

        self.snmp_engine.get_table(host, '1.3.6.1.2.1.2.2.1.1', my_callback1, table_trim=1, obj=self )
        self.poll()
        eq_(len(self.results),2)
        eq_(len(self.results[1]),table_length)
        for oid,val in self.results[1].items():
            assert(oid == val)

    def test_v2_table(self):
        """ SNMP v2 table fetch - uses ifTable.ifIndex """
        host = DummyHost("127.0.0.1", 2, "public")
        #self.snmp_engine.set_default_timeout(1)
        # Get size of iftable
        self.snmp_engine.get_int(host, '1.3.6.1.2.1.2.1.0', my_callback1, obj=self)
        self.poll()
        eq_(len(self.results),1)
        table_length = self.results[0]

        self.snmp_engine.get_table(host, '1.3.6.1.2.1.2.2.1.1', my_callback1, table_trim=1, obj=self )
        self.poll()
        eq_(len(self.results),2)
        eq_(len(self.results[1]),table_length)
        for oid,val in self.results[1].items():
            assert(oid == val)
