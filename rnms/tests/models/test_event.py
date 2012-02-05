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
""" Test suite for the Event model in Rosenberg"""
from nose.tools import eq_

from rnms import model
from rnms.tests.models import ModelTest

class TestEvent(ModelTest):
    klass = model.Event
    test_event_type = model.EventType(u'Test EventType')


    attrs = dict(
            event_type = test_event_type,
        #    attribute = test_attribute
            )

    def do_get_dependencies(self):
        test_user = model.User()
        test_user.display_name = u'Test User'
        test_user.user_name = 'testuser'
        test_user.email_address = 'test@email'
        test_host = model.Host(display_name=u'Test Host')
        
        test_attribute = model.Attribute(display_name='TestAtt')

        test_attribute.user = test_user
        return{'attribute': test_attribute, 'host': test_host}

    def test_text_simple(self):
        """ Event simple text test """
        self.test_event_type.text = u'test text'
        eq_(self.obj.text(), u'test text')

    def test_text_subs(self):
        """ Event text with attribute and host shows display name. """
        self.test_event_type.text = u'start <host> <attribute> end'
        eq_(self.obj.text(), u'start Test Host TestAtt end')

    def test_text_client(self):
        """ Event text with client shows user display name. """
        self.test_event_type.text = u'start <client> end'
        eq_(self.obj.text(), u'start Test User end')


class TestEventType(ModelTest):
    klass = model.EventType
    attrs = dict(
            display_name = (u'Test EventType'),
            )

    def test_obj_creation_displayname(self):
        """The EventType constructor must set the display name right"""
        eq_(self.obj.display_name, u'Test EventType')

    def test_getting_by_name(self):
        """ EventType must be fetchable by its display name"""
        test_et = model.EventType.by_name(u'Test EventType')
        eq_(test_et, self.obj)

    def test_getting_by_id(self):
        """ EventType must be fetchable by its id"""
        test_et = model.EventType.by_id(self.obj.id)
        eq_(test_et, self.obj)
