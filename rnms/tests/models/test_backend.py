# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012-2014 Craig Small <csmall@enc.com.au>
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
        display_name=(u'Test Backend'),
        command='test_command',
        )

    def test_backend_str(self):
        """Backend  shows corect string """
        eq_(str(self.obj), '<Backend name=Test Backend command=test_command>')

    def test_backend_init_plugin(self):
        """Backend init sets plugin name correctly"""
        eq_(self.obj.command, 'test_command')

    def test_default_backend(self):
        """ Return default backend """
        default_backend = self.obj.default()
        eq_(default_backend, self.obj)
        eq_(default_backend.id, 1)
