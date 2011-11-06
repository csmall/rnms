# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
from nose.tools import eq_

from rnms import model
from rnms.tests.models import ModelTest

class TestAttribute(ModelTest):
    """Unit test case for the ``Attribute`` model."""
    klass = model.Attribute
    attrs = dict(
        #attribute_type = model.AttributeType(display_name='Test AType'),
        display_name = u"Test Attribute"
        )

    def test_attrib_init_displayname(self):
        """Attribute display name set by init"""
        eq_(self.obj.display_name, u'Test Attribute')

