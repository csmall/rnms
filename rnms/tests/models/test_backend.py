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
import mock

from rnms import model
from rnms.tests.models import ModelTest

test_poller_row = mock.Mock(spec_set=model.PollerRow)

class TestBackend(ModelTest):
    klass = model.Backend
    attrs = dict(
            display_name = (u'Test Backend'),
            command = 'test',
            #position = 1,
            )

    def setUp(self):
        super(TestBackend, self).setUp()

    def test_run_none(self):
        """Backend none reutrns blank """
        self.obj.command = 'none'
        eq_('',self.obj.run(test_poller_row, None, ''))

    def test_run_invalid(self):
        """ Invalid backend type returns error"""
        self.obj.command = 'f00b@r'
        eq_('invalid backend {0}'.format(self.obj.command), self.obj.run(test_poller_row, None, ''))

    def test_run_admin_direct(self):
        """ admin_status backend sets status correctly """
        self.obj.command = 'admin_status'
        self.obj.parameters = None
        att = model.Attribute(display_name=u'Test Attribute')
        for newstate in ['up','down', 'testing']:
            eq_('Admin status set to {0}'.format(newstate), self.obj.run(test_poller_row, att, newstate))


    def test_admin_badvalue(self):
        """ admin_status backend detects bad values """
        self.obj.command = 'admin_status'
        self.obj.parameters = None
        att = model.Attribute(display_name=u'Test Attribute')
        att.admin_state = 0
        eq_("Bad Admin status \"foo\"",self.obj.run(test_poller_row, att, 'foo'))
        eq_(att.admin_state, 0)

    def test_admin_nochange(self):
        """ admin_status backend doesnt change if same """
        self.obj.command = 'admin_status'
        self.obj.parameters = None
        att = model.Attribute(display_name=u'Test Attribute')
        att.admin_state = 1
        eq_("Admin status not changed",self.obj.run(test_poller_row, att, 'up'))
