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
from rnms.tests.models import ModelTest


class TestPoller(ModelTest):
    klass = model.Poller
    attribute = model.Attribute(display_name=u'Test Attribute')
    attrs = dict(
        display_name=(u'Test Poller'),
        command=('test_poller')
        )
    poller_row = mock.Mock()
    pobj = mock.Mock()

    def test_poller_init_name(self):
        """Poller init sets display name correctly"""
        eq_(self.obj.display_name, u'Test Poller')

    def test_poller_init_plugin(self):
        """Poller init sets plugin name correctly"""
        eq_(self.obj.command, 'test_poller')


class TestBackend(ModelTest):
    klass = model.Backend
    attrs = dict(
        display_name=u'Test Backend',
        command='test_backend'
        )


class TestPollerSet(ModelTest):
    klass = model.PollerSet
    attrs = dict(
        display_name=u'Test Poller Set',
        )

    def test_pollerset_init_name(self):
        """PollerSet init sets display name correctly"""
        eq_(self.obj.display_name, u'Test Poller Set')

    def test_pollerset_empty(self):
        """PollerSet is initially empty"""
        eq_(len(self.obj.poller_rows), 0)

    def test_pollerset_insert_first(self):
        """ PollerSet insert_first puts new rows first"""
        first_row = model.PollerRow()
        second_row = model.PollerRow()
        self.obj.insert(0, first_row)
        eq_(len(self.obj.poller_rows), 1)
        eq_(first_row.position, 0)
        self.obj.insert(0, second_row)
        eq_(len(self.obj.poller_rows), 2)
        eq_(first_row.position, 1)
        eq_(second_row.position, 0)

    def test_pollerset_insert_last(self):
        """ PollerSet insert_first puts new rows last"""
        first_row = model.PollerRow()
        second_row = model.PollerRow()
        self.obj.insert(0, first_row)
        eq_(len(self.obj.poller_rows), 1)
        eq_(first_row.position, 0)
        self.obj.append(second_row)
        eq_(len(self.obj.poller_rows), 2)
        eq_(first_row.position, 0)
        eq_(second_row.position, 1)

    def test_pollerset_row_to(self):
        """ PollerSet row_to relocates third row to position 3"""
        first_row = model.PollerRow()
        second_row = model.PollerRow()
        third_row = model.PollerRow()
        self.obj.insert(0, first_row)
        self.obj.append(second_row)
        self.obj.append(third_row)
        eq_(len(self.obj.poller_rows), 3)
        eq_(first_row.position, 0)
        eq_(second_row.position, 1)
        eq_(third_row.position, 2)

        self.obj.row_to(1, third_row)
        eq_(len(self.obj.poller_rows), 3)
        eq_(first_row.position, 0)
        eq_(second_row.position, 2)
        eq_(third_row.position, 1)

    def test_pollerset_row_swap(self):
        """ PollerSet row_swap swaps rows 2 and 3"""
        first_row = model.PollerRow()
        second_row = model.PollerRow()
        third_row = model.PollerRow()
        self.obj.insert(0, first_row)
        self.obj.append(second_row)
        self.obj.append(third_row)
        eq_(len(self.obj.poller_rows), 3)
        eq_(first_row.position, 0)
        eq_(second_row.position, 1)
        eq_(third_row.position, 2)

        self.obj.row_swap(1, 2)
        eq_(len(self.obj.poller_rows), 3)
        eq_(first_row.position, 0)
        eq_(second_row.position, 2)
        eq_(third_row.position, 1)


class TestPollerRow(ModelTest):
    klass = model.PollerRow

    def do_get_dependencies(self):
        poller_set = model.PollerSet(display_name=u'Test PollerSet')
        return{'poller_set': poller_set}
