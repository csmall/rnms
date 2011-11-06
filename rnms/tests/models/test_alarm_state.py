# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
from nose.tools import eq_

from rnms import model
from rnms.tests.models import ModelTest

class TestAlarmState(ModelTest):
    """Unit test case for the ``AlarmState`` model."""
    klass = model.AlarmState
    attrs = dict(
        display_name = u"Test AlarmState",
        internal_state = 1
        )

    def test_astate_init_displayname(self):
        """AlarmState display name set by init"""
        eq_(self.obj.display_name, u'Test AlarmState')

    def test_astate_by_name(self):
        """AlarmState can be fetched by display name. """
        new_astate = model.AlarmState.by_name(u'Test AlarmState')
        eq_(new_astate, self.obj)

