# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012 Craig Small <csmall@enc.com.au>
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
from nose.tools import eq_

from rnms import model
from rnms.tests.models import ModelTest

# Needed for a zone
class TestSlaRow(ModelTest):
    klass = model.SlaRow

    def do_get_dependencies(self):
        sla = model.Sla(display_name=u'Test SLA')
        return {'sla': sla}

    def test_sla_row_operators(self):
        """SLA Row operators test"""
        self.obj.limit=100

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

    def test_sla_row_eval(self):
        """SLA Row eval test"""
        rrd_values = {'one': 1.0, 'two': 2, 'fifty': 50.0, 'one_hundred': 100.0,
                'answer': 42, 'other': 58}
        attrib = model.Attribute()
        self.obj.limit=50
        self.obj.oper = '='
        eval_tests = (
                ('${fifty}', True),
                ('${answer}', False),
                ('${one_hundred} / ${two}', True),
                ('( ${one_hundred} + ${two} ) / ${two}', False),
                ('${answer} + ${other} / ${two}', False),
                ('( ${answer} + ${other} ) / ${two}', True),
                ('(${answer}+${other})/${two}', True), # no space
                ('${answer} + 8', True),
                )
        for (expr,result) in eval_tests:
            self.obj.expression = expr
            eval_result = self.obj.eval(rrd_values)
            eq_(eval_result[0], result)

