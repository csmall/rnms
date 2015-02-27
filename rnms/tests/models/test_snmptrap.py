# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2014-2015 Craig Small <csmall@enc.com.au>
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
"""Test suite SnmpTrap model """

from nose.tools import eq_

from rnms import model
from rnms.tests.models import ModelTest


class TestAttribute(ModelTest):
    """Unit test case for the ``SnmpTrap`` model."""
    klass = model.SnmpTrap
    attrs = dict(
        host_id=1,
        trap_oid='1.2.3.4.5'
        )

    def test_repr(self):
        """ SnmpTest returns correct repr """
        eq_(str(self.obj), '<SNMP Trap host=none varbinds=0>')

    def test_add_varbind(self):
        """ SnmpTrap can add varbind """
        self.obj.set_varbind('4.3.2.1', '42')
        eq_(len(self.obj.varbinds), 1)

    def test_query_empty_varbind(self):
        """ SnmpTrap with no varbinds returns None """
        eq_(self.obj.get_varbind('4.3.2.1'), None)

    def test_query_varbind(self):
        """ SnmpTrap returns varbind value """
        self.obj.set_varbind('4.3.2.1', '9919')
        self.obj.set_varbind('4.3.2', 'WRONG')
        eq_(len(self.obj.varbinds), 2)
        eq_(self.obj.get_varbind('4.3.2.1'), '9919')
