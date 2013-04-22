# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012,2013 Craig Small <csmall@enc.com.au>
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
from rnms.lib import states

test_poller_row = mock.MagicMock(spec_set=model.PollerRow)
test_attribute = model.Attribute(display_name = u'Test Attribute')

class TestBackend(ModelTest):
    klass = model.Backend
    attrs = dict(
            display_name = (u'Test Backend'),
            command = 'test_command',
            )

    def test_backend_str(self):
        """Backend  shows corect string """
        eq_(str(self.obj), '<Backend name=Test Backend command=test_command>')

    def test_backend_init_plugin(self):
        """Backend init sets plugin name correctly"""
        eq_(self.obj.command,'test_command')

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
        test_attribute.admin_state = states.STATE_UNKNOWN
        for newstate in ['up','down', 'testing']:
            eq_('Admin status set to {0}'.format(newstate),
                self.obj.run(test_poller_row, test_attribute, newstate))


    def test_admin_badvalue(self):
        """ admin_status backend detects bad values """
        self.obj.command = 'admin_status'
        self.obj.parameters = None
        test_attribute.admin_state = states.STATE_UP
        eq_("Bad Admin status \"foo\"",self.obj.run(test_poller_row,
                                                    test_attribute, 'foo'))
        eq_(test_attribute.admin_state, states.STATE_UP)

    def test_run_event_always(self):
        """ Backend event_always works correctly """
        self.obj.command = 'event_always'
        self.obj._run_event = mock.Mock(return_value="Hello, World!")
        self.obj._run_event.assert_run_once_with('hh')
        eq_(self.obj.run(test_poller_row, test_attribute, 'up'), "Hello, World!")

    def test_admin_nochange(self):
        """ admin_status backend doesnt change if same """
        self.obj.command = 'admin_status'
        self.obj.parameters = None
        test_attribute.admin_state = states.STATE_UP
        eq_("Admin status not changed",self.obj.run(test_poller_row,
                                                    test_attribute, 'up'))

    def test_default_backend(self):
        """ Return default backend """
        default_backend = self.obj.default()
        eq_(default_backend, self.obj)
        eq_(default_backend.id, 1)
