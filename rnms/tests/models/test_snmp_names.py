# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
import mock 

from nose.tools import eq_

from rnms import model
from rnms.tests.models import ModelTest

test_device = mock.MagicMock(spec_set=model.SNMPDevice)
test_device.display_name = u'Test Device'

class TestSNMPEnterprise(ModelTest):
    """ Unit test case for the ``SNMPEnterprise'' model."""
    klass = model.SNMPEnterprise
    attrs = dict (
            id = 1,
            display_name = u'Test Enterprise'
            )

    def test_by_id(self):
        """ SNMP Enterprise can be fetched by enterprise ID """
        new_ent = model.SNMPEnterprise.by_id(1)
        eq_(new_ent, self.obj)

    def test_oid2name_none(self):
        """ SNMP Enterprise with no oid returns unknown """
        eq_(self.obj.oid2name(None), ('unknown', ''))

    def test_oid2name_empty(self):
        """ SNMP Enterprise with empty oid returns unknown """
        eq_(self.obj.oid2name(''), ('unknown', ''))

    def test_oid2name_badid(self):
        """ SNMP Enterprise with bad oid returns unknown """
        eq_(self.obj.oid2name('999.1.2.3'), ('unknown',''))
    
    def test_oid2name_noid(self):
        """ SNMP Enterprise with not found enterprise """
        eq_(self.obj.oid2name('ent.999.1.2.3'), ('unknown vendor 999',''))
    
    def test_oid2name_short(self):
        """ SNMP Enterprise with not found enterprise """
        self.obj.device_offset=99
        eq_(self.obj.oid2name('ent.1.2.3'), ('Test Enterprise',''))
    
    def test_oid2name_unkdevice(self):
        """ SNMP Enterprise with unknown device """
        self.obj.device_offset=2
        eq_(self.obj.oid2name('ent.1.2.3.4.5'), ('Test Enterprise','unknown 3.4.5'))
    
    def test_oid2name_ok(self):
        """ SNMP returns correct enterprise and device name """
        old_by_id = model.snmp_names.SNMPDevice.by_id
        model.snmp_names.SNMPDevice.by_id = mock.Mock(return_value=test_device)
        eq_(self.obj.oid2name('ent.1.2.3.4.5'), ('Test Enterprise','Test Device'))
        model.snmp_names.SNMPDevice.by_id = old_by_id
        
    def test_oid2name_numeric(self):
        """ SNMP Entrprise with numeric prefix """
        old_by_id = model.snmp_names.SNMPDevice.by_id
        model.snmp_names.SNMPDevice.by_id = mock.Mock(return_value=test_device)
        self.obj.device_offset=2
        eq_(self.obj.oid2name('1.3.6.1.4.1.1.2.3.4.5'), ('Test Enterprise','Test Device'))
        model.snmp_names.SNMPDevice.by_id = old_by_id
