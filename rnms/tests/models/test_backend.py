# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012 Craig Small <csmall@enc.com.au>
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
""" Test suite for the backend model in Rosenberg"""
from nose.tools import eq_

from rnms import model
from rnms.tests.models import ModelTest

class TestBackend(ModelTest):
    klass = model.Backend
    attrs = dict(
            display_name = (u'Test Backend'),
            plugin_name = 'test',
            command = 'test',
            #position = 1,
            )

    def test_run_none(self):
        """Backend none reutrns blank """
        self.obj.command = 'none'
        eq_('',self.obj.run(None, ''))

    def test_run_invalid(self):
        """ Invalid backend type returns error"""
        self.obj.command = 'f00b@r'
        eq_('invalid backend', self.obj.run(None, ''))

    def test_run_admin_direct(self):
        """ admin_status backend sets status correctly """
        self.obj.command = 'admin_status'
        self.obj.parameters = None
        att = model.Attribute(display_name=u'Test Attribute')
        for newstate in [0,1,2,3]:
            eq_('Admin status set to {0}'.format(newstate), self.obj.run(att, newstate))
            eq_(att.admin_state, newstate)

    def test_run_admin_outrange(self):
        """ admin_status backend out of range poller result doesnt set status """
        self.obj.command = 'admin_status'
        self.obj.parameters = None
        att = model.Attribute(display_name=u'Test Attribute')
        att.admin_state = 0
        eq_("New State -1 must be 0 to 3",self.obj.run(att, -1))
        eq_(att.admin_state, 0)
        eq_("New State 4 must be 0 to 3",self.obj.run(att, 4))
        eq_(att.admin_state, 0)

    def test_admin_badvalue(self):
        """ admin_status backend detects bad values """
        self.obj.command = 'admin_status'
        self.obj.parameters = None
        att = model.Attribute(display_name=u'Test Attribute')
        att.admin_state = 0
        eq_("New State foo must be an integer",self.obj.run(att, 'foo'))
        eq_(att.admin_state, 0)

    def test_admin_nochange(self):
        """ admin_status backend doesnt change if same """
        self.obj.command = 'admin_status'
        self.obj.parameters = None
        att = model.Attribute(display_name=u'Test Attribute')
        att.admin_state = 0
        eq_("Admin status not changed",self.obj.run(att, 0))
