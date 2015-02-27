# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2011-2015 Craig Small <csmall@enc.com.au>
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
""" Test suite for the Poller and PollerSet model in RoseNMS"""
from nose.tools import eq_
import mock

from rnms import model
from rnms.lib.poller.poller_model import CachePoller


class TestCachePoller(object):

    def setUp(self):
        db_poller = mock.MagicMock(spec_set=model.Poller)
        db_poller.command = 'buffer'
        db_poller.parameters = ''
        self.obj = CachePoller(db_poller)
        self.poller_row = {}
        self.pobj = mock.Mock()
        self.attribute = model.Attribute(display_name=u'Test Attribute')

    def test_poller_run(self):
        """ Poller run command works"""
        poller_buffer = {}
        poller_output = self.obj.run(
            self.poller_row, self.pobj, self.attribute, poller_buffer)
        eq_(poller_output, False)  # FIXME
