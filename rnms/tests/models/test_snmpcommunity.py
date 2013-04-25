# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>
#
""" Test suite for the Host model in Rosenberg"""
from nose.tools import eq_, assert_true, assert_false

from rnms import model
from rnms.tests.models import ModelTest

# Needed for a zone
class TestZone(ModelTest):
    klass = model.SnmpCommunity
    attrs = dict(
            display_name = (u'Test Community'),
            )

    def test_by_address(self):
        """ Community can correctly be fetched by display_name """
        new_comm = model.SnmpCommunity.by_name(u'Test Community')
        eq_(new_comm, self.obj)

    def test_v1_is_v1(self):
        """ SNMP v1 community returns True for ro_is_snmpv1 """
        self.obj.readonly = ('1', 'test')
        assert_true(self.obj.ro_is_snmpv1())

    def test_v1_is_not_v2(self):
        """ SNMP v1 community returns False for ro_is_snmpv2 """
        self.obj.readonly = ('1', 'test')
        assert_false(self.obj.ro_is_snmpv2())

    def test_v2_is_not_v1(self):
        """ SNMP v2 community returns False for ro_is_snmpv1 """
        self.obj.readonly = ('2', 'test')
        assert_false(self.obj.ro_is_snmpv1())

    def test_v2_is_v2(self):
        """ SNMP v2 community returns True for ro_is_snmpv2 """
        self.obj.readonly = ('2', 'test')
        assert_true(self.obj.ro_is_snmpv2())

