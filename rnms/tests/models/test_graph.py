# -*- coding: utf-8 -*-
"""Test suite for the TG app's models"""
import mock
from nose.tools import eq_, raises, assert_true, assert_false

from rnms import model
from rnms.tests.models import ModelTest

#test_attribute_type = model.AttributeType()
#test_attribute_type.display_name = u'Test Attribute Type'
#test_attribute_type.rra_cf = mock.Mock(return_value='AVERAGE')

#test_attribute = mock.MagicMock(spec=model.Attribute)
#test_attribute.attribute_type = test_attribute_type

test_epoch = 55689300.0
test_epoch_str = str(test_epoch)
test_color = 'aa00ff'

class TestGraph(ModelTest):
    klass = model.GraphType
    attrs = dict(
        display_name = u'Test Graph',
        title = u'Test Title',
    )
    def do_get_dependencies(self):
        attribute_type = model.AttributeType()
        attribute_type.display_name = u'Test Attribute Type'
        return {'attribute_type':attribute_type}

    def test_by_id(self):
        """ GraphType fetched by ID """
        graph_type = model.GraphType.by_id(1)
        eq_(graph_type, self.obj)

    def test_by_name(self):
        """ GraphType fetched by name """
        graph_type = model.GraphType.by_display_name(u'Test Graph')
        eq_(graph_type, self.obj)

#class TestGraphLine(ModelTest):
#    """Unit test case for the ``GraphTypeLine`` model."""
#    klass = model.GraphTypeLine


