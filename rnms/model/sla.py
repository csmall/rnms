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
""" Service Level Agreements - Checks the values of AttributeTypeField"""

import logging
import operator
import re

from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, Boolean, String, SmallInteger
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, DBSession, Event
from rnms.lib.parsers import RnmsTextTemplate, NumericStringParser
from rnms.lib.genericset import GenericSet

logger = logging.getLogger('rnms')

class Sla(DeclarativeBase, GenericSet):
    __tablename__ = 'slas'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    display_name = Column(Unicode(60), nullable=False, unique=True)
    event_text = Column(Unicode(60))
    threshold = Column(SmallInteger)
    event_type_id = Column(Integer,ForeignKey('event_types.id'))
    event_type = relationship('EventType', order_by='EventType.id', backref='slas')
    alarm_state_id = Column(Integer,ForeignKey('alarm_states.id'))
    alarm_state = relationship('AlarmState', order_by='AlarmState.id', backref='slas')
    sla_rows = relationship('SlaRow', backref=backref('sla', lazy='joined'), order_by='SlaRow.position')
    #}
    field_re = re.compile(r'<([a-z0-9_-]+)>')

    def __init__(self):
        self.rows = self.sla_rows

    def insert(self, new_pos, new_row):
        new_row.sla = self
        GenericSet.insert(self,new_pos, new_row)

    def append(self, new_row):
        new_row.sla = self
        GenericSet.append(self,new_row)

    def _update_rrd_values(self, rrd_values, attribute, text, start_time, end_time):
        """
        Given a string and existing rrd_values dictionary, add in the
        missing values
        """
        new_fields = set(self.field_re.findall(text))
        for new_field in new_fields:
            if new_field not in rrd_values:
                rrd_values[new_field] = attribute.fetch_rrd_value(start_time, end_time, new_field)
        return rrd_values

    def analyze(self, attribute):
        """
        Analyze this SLA against the given attribute
        """
        time_end = 10
        time_span = 30
        start_time = (time_span-5+time_end) * 60
        end_time = time_end * 60

        rrd_values = attribute.get_fields()
        cond_results=[]
        event_details=[]
        cond_rows = DBSession.query(SlaRow).filter(SlaRow.sla_id==self.id)
        cond_row_count = 0
        for cond_row in cond_rows:
            cond_row_count += 1
            cond = cond_row.sla_condition
            rrd_values = self._update_rrd_values(rrd_values, attribute, cond.expression, start_time, end_time)
            if len(rrd_values) == 0:
                return
            # AND/OR remove the last two items from stack and replace with reasult
            if (cond.expression == 'AND'):
                if len(cond_results) < 2:
                    logger.error('AND sla condition needs 2 results')
                    continue
                result = cond_results[-1] and cond_results[-2]
                logger.info('A%d Row%d: %s AND %s := %s',attribute.id, cond_row_count, cond_results[-1], cond_results[-2], result)
                cond_results = cond_results[:-2] + [result]
            elif (cond.expression == 'OR'):
                if len(cond_results) < 2:
                    logger.error('OR sla condition needs 2 results')
                    continue
                result = cond_results[-1] or cond_results[-2]
                logger.info('A%d Row%d: %s OR %s := %s',attribute.id, cond_row_count, cond_results[-1], cond_results[-2], result)
                cond_results = cond_results[:-2] + [result]
            else:
                (result, details) = cond.eval(rrd_values)
                logger.info('A%d Row%d: %s := %s', attribute.id, cond_row_count, details, result)
                cond_results.append(result)
                if result != False:
                    event_details.append(details)
        logger.info("A%d VALUES %s",attribute.id, ', '.join(['{0}({1})'.format(k,v) for (k,v) in rrd_values.items()]))
        if (len(cond_results) < 1 or cond_results[-1] == False):
            logger.info('A%d: Final Result: False', attribute.id)
        else:
            logger.info('A%d: Final Result: True', attribute.id)
            event_fields={
                    'info': self.event_text,
                    'details': ', '.join(event_details)}
            new_event = Event(event_type=self.event_type, attribute=attribute, alarm_state=self.alarm_state, field_list=event_fields)
            DBSession.add(new_event)
            new_event.process()

class SlaRow(DeclarativeBase):
    """
    A single row for a SLA that uses a specific SlaCondition
    """
    __tablename__ = 'sla_rows'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    sla_id = Column(Integer, ForeignKey('slas.id'), nullable=False)
    position = Column(Integer, nullable=False, default=1)
    show_result = Column(Boolean, nullable=False, default=True)
    sla_condition_id = Column(Integer, ForeignKey('sla_conditions.id'))
    sla_condition = relationship('SlaCondition', lazy='joined')

    def __init__(self,sla=None, sla_condition=None, show_result=True, position=1):
        self.sla = sla
        self.sla_condition = sla_condition
        self.show_result = show_result
        self.position = position

    def __repr__(self):
        if self.sla is not None:
            sla_name = self.sla.display_name
        else:
            sla_name = 'None'
        if self.sla_condition is not None:
            cond_name = self.sla_condition.display_name
        else:
            cond_name = 'None'
        return '<SlaRow position={0} sla={1} conditiion={2}'.format(self.position, sla_name, cond_name)

class SlaCondition(DeclarativeBase):
    __tablename__ = 'sla_conditions'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(60), nullable=False, unique=True)
    expression = Column(String(250))
    oper = Column(Unicode(5))
    limit = Column(Integer)
    show_info = Column(Unicode(60))
    show_expression = Column(Unicode(250))
    show_unit = Column(Unicode(60))

    allowed_opers={
            '=' : operator.eq,
            '<>': operator.ne,
            '>' : operator.gt,
            '<' : operator.lt,
            '>=': operator.ge,
            '<=': operator.le}

    def operate(self, output):
        """
        Given the calculated output, run the operator against our limit.
        This function does things like > limit etc
        """
        try:
            output = int(float(output))
        except ValueError:
            return False
        if (self.oper not in self.allowed_opers):
            logger.error('Invalid operator "%s"', self.oper)
            return False
        return self.allowed_opers[self.oper](output,self.limit)

    def eval(self, rrd_values):
        """
        Evaluate this specific SLA condition against the given attribute
        """
        nsp = NumericStringParser()
        text_template = RnmsTextTemplate(self.expression)
        parsed_expression = text_template.safe_substitute(rrd_values)
        expression_output = nsp.eval(parsed_expression)
        try:
            expression_output = nsp.eval(parsed_expression)
        except:
            logger.error("Cannot parse \"%s\" (%s)", parsed_expression, rrd_values)
            return (False, 'error')
        return (self.operate(expression_output),
                "{0} ({1}) {2} {3}".format(parsed_expression, expression_output, self.oper, self.limit))



