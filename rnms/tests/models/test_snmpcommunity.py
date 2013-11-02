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


class TestCommunity(ModelTest):
    klass = model.SnmpCommunity
    attrs = {'display_name': u'Test Community'}

    def test_by_address(self):
        """ Community can correctly be fetched by display_name """
        new_comm = model.SnmpCommunity.by_name(u'Test Community')
        eq_(new_comm, self.obj)

    def test_empty_community(self):
        """ Empty community returns true for is_empty """
        self.obj.community = ''
        assert_true(self.obj.is_empty())

    def test_v1_setup(self):
        """ SNMP v1 community setup correctly """
        self.obj.set_v1community('test')
        eq_(self.obj.version, 1)
        assert_true(self.obj.is_snmpv1())
        assert_false(self.obj.is_snmpv2())

    def test_v2_setup(self):
        """ SNMP v2 community setup correctly """
        self.obj.set_v2community('test')
        eq_(self.obj.version, 2)
        assert_false(self.obj.is_snmpv1())
        assert_true(self.obj.is_snmpv2())

    def test_v3_auth_none_setup(self):
        """ SNMP v3 with no auth setup correctly """
        self.obj.set_v3auth_none()
        eq_(self.obj.version, 3)
        assert_false(self.obj.is_snmpv1())
        assert_false(self.obj.is_snmpv2())

    def test_v3_auth_md5(self):
        """ SNMP v3 with md5 setup correctly """
        self.obj.set_v3auth_md5('username', 'password')
        eq_(self.obj.version, 3)
        assert_false(self.obj.is_snmpv1())
        assert_false(self.obj.is_snmpv2())
        eq_(self.obj.security_name, 'username')

