# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011 Craig Small <csmall@enc.com.au>
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
""" Test suite for the Zone model in Rosenberg"""
from nose.tools import eq_

from rnms import model
from rnms.tests.models import ModelTest

class TestZone(ModelTest):
    klass = model.Zone
    attrs = dict(
            display_name = (u'Test Zone'),
            short_name = (u'test')
            )

    def test_obj_creation_displayname(self):
        """The obj constructor must set the display name right"""
        eq_(self.obj.display_name, u'Test Zone')

    def test_obj_creation_shortname(self):
        """The obj constructor must set the short name right"""
        eq_(self.obj.short_name, u'test')

    def test_getting_by_name(self):
        """ Zone must be fetchable by its display name"""
        test_zone = model.Zone.by_name(u'Test Zone')
        eq_(test_zone, self.obj)

#    def test_getting_default(self):
#        """ Default Zone must be fetchable. """
#        default_zone = model.Zone.default()
#        eq_(default_zone, self.obj)

