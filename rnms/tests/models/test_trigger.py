# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
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
""" Test suite for the SLA model in Rosenberg"""
import mock

from nose.tools import eq_, raises

from rnms import model
from rnms.tests.models import ModelTest

class TestTrigger(ModelTest):
    klass = model.Trigger
    attrs = dict( display_name = u'Test Trigger' )

    @raises(ValueError)
    def test_bad_match_type(self):
        """ Trigger with bad match_type raises exception """
        dumm = model.Trigger(match_type='bad')

    def test_repr(self):
        """ Trigger has correct repr """
        eq_(str(self.obj), '<Trigger name=Test Trigger rules=0>')

    def test_rows_empty(self):
        """Trigger Rules is initially empty"""
        eq_(len(self.obj.rules),0)

    def test_triggerrules_insert_first(self):
        """ Trigger rules insert_first puts new rows first"""
        first_row = model.TriggerRule()
        second_row = model.TriggerRule()
        self.obj.insert(0,first_row)
        eq_(len(self.obj.rules),1)
        eq_(first_row.position,0)
        self.obj.insert(0,second_row)
        eq_(len(self.obj.rules),2)
        eq_(first_row.position,1)
        eq_(second_row.position,0)

    def test_triggerruleds_insert_last(self):
        """ Trigger rules insert_first puts new rows last"""
        first_row = model.TriggerRule()
        second_row = model.TriggerRule()
        self.obj.insert(0,first_row)
        eq_(len(self.obj.rules),1)
        eq_(first_row.position,0)
        self.obj.append(second_row)
        eq_(len(self.obj.rules),2)
        eq_(first_row.position,0)
        eq_(second_row.position,1)

    def test_match_type_alarm(self):
        """ Trigger returns correct match_type name for alarm """
        self.obj.match_type = 0
        eq_(self.obj.match_type_name(), 'alarm')

    def test_match_type_event(self):
        """ Trigger returns correct match_type name for event """
        self.obj.match_type = 1
        eq_(self.obj.match_type_name(), 'event')

class TestTriggerRule(ModelTest):
    klass = model.TriggerRule

    def do_get_dependencies(self):
        trigger = model.Trigger(display_name=u'Test SLA')
        return {'trigger': trigger}

    def test_trigger_row_operators(self):
        """Trigger Rule operators test"""
        self.obj.limit='100'

        operator_tests=(
                (1,'=',False), (100,'=',True),
                (1,'<>',True), (100,'<>',False),
                (99,'>',False), (100,'>',False), (101,'>',True),
                (99,'>=',False), (100,'>=',True), (101,'>=',True),
                (99,'<',True), (100,'<',False), (101,'<',False),
                (99,'<=',True), (100,'<=',True), (101,'<=',False),
                )
        for (output,op,result) in operator_tests:
            self.obj.oper= op
            op_result = self.obj.operate(output)
            eq_(op_result, result)

    def test_eval_group_operators(self):
        """ Triger Rule group operators """
        operator_tests = (
                (1, 'IN', '1,2,3', True), (4, 'IN', '1,2,3', False),
                (4, '!IN', '1,2,3', True), (1, '!IN', '1,2,3', False),
                ('dog', 'C', 'the dog barks', True),  
                ('cat', 'C', 'the dog barks', False),  
                ('cat', '!C', 'the dog barks', True),  
                ('dog', '!C', 'the dog barks', False),  
                )
        for (output,op,limit,result) in operator_tests:
            self.obj.oper = op
            self.obj.limit = limit
            op_result = self.obj.operate(output)
            eq_(op_result, result)

    def test_bad_operator(self):
        """ Bad operator returns False """
        self.obj.oper = 'BAD'
        self.obj.limit = 100
        eq_(self.obj.operate(100), False)

    def test_trigger_eval_prev_or(self):
        """ Trigger Rule eval previous True with OR """
        self.obj.and_rule = False
        eq_(self.obj.eval(True, None), True)
    
    def test_trigger_eval_prev_and(self):
        """ Trigger Rule eval previous True with AND """
        self.obj.and_rule = True
        eq_(self.obj.eval(True, None), False)

    def test_trigger_eval_operate(self):
        """ Trigger Rule eval various tests """
        eval_tests = (
                # prev_value, and_rule, this_value, result
                ( False, 'and' , False, False),
                ( False, 'or', False, False),
                ( True, 'and', False, False),
                ( True, 'or', False, True),
                ( True, 'and', True, True),
                ( True, 'or', True, True)
                )
        self.obj._get_alarm_field = mock.Mock(return_value=1)
        for (pval, and_rule, cval, result) in eval_tests:
            self.obj.and_rule = (and_rule == 'and')
            self.obj.operate = mock.Mock(return_value=cval)
            eq_(self.obj.eval(pval, None), result)


    def test_init_rule_field(self):
        """ TriggerRule with field sets field """
        new_rule = model.TriggerRule(field='attribute_name')
        eq_(new_rule.field, 1)

    @raises(ValueError)
    def test_init_rule_bad_field(self):
        """ TriggerRule init with bad field name raises ValueError """
        new_rule = model.TriggerRule(field='BAD')


    def test_field_name(self):
        """ TriggerRule returns correct field name """
        self.obj.field = 2
        eq_(self.obj.field_name(), 'hour')
