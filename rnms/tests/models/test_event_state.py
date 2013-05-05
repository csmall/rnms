# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
from nose.tools import eq_

from rnms import model
from rnms.tests.models import ModelTest

class TestEventState(ModelTest):
    """Unit test case for the ``EventState`` model."""
    klass = model.EventState
    attrs = dict(
        display_name = u"Test EventState",
        internal_state = 1
        )

    def do_get_dependencies(self):
        test_severity = model.Severity()
        test_severity.display_name = u'Test Severity'
        return {'severity': test_severity}

    def test_estate_init_displayname(self):
        """EventState display name set by init"""
        eq_(self.obj.display_name, u'Test EventState')

    def test_estate_by_name(self):
        """EventState can be fetched by display name. """
        new_estate = model.EventState.by_name(u'Test EventState')
        eq_(new_estate, self.obj)

