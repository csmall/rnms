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

""" Trigger model """
from sqlalchemy import ForeignKey, Column
from sqlalchemy import relationship
from sqlalchemy.types import Integer, Unicode, SmallInteger, Boolean

from rnms.model import DeclarativeBase, DBSession
from rnms.lib.genericset import GenericSet

match_types=('Alarm', 'Event')
trigger_fields=('Active', 'Attribute', 'Attribute Type', 'Attribute Name', 'Hour', 'Type', 'Duration', 'Host', 'Map', 'Client', 'None')
rule_operators=('=', '<>', '>', '<', '>=', '<=', 'IN', '!IN', 'C', '!C')

class Trigger(DeclarativeBase, GenericSet):
    __tablename__ = 'triggers'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    match_type = Column(SmallInteger)
    rules = relationship('TriggerRule', order_by='TriggerRule.position')
    #}

    def __init__(self, display_name=None, match_type=None):
        self.display_name = display_name
        if match_type is not None:
            if match_type is not match_types:
                raise ValueError('match_type must be Event or Alarm')
            self.match_type = match_types.index(match_type)

        self.rows = self.rules

    def __repr__(self):
        return '<Trigger name=%s rules=%d>' % (self.display_name,len(self.rules))

    def insert(self, new_pos, new_row):
        new_row.trigger = self
        GenericSet.insert(self,new_pos, new_row)

    def append(self, new_row):
        new_row.trigger = self
        GenericSet.append(self,new_row)

    def process_alarm(self, alarm):
        """
        Attempt to raise a trigger based upon this alarm
        """
        rule_result = None
        for rule in self.rules:
            rule_result = rule.process_alarm(rule_result, alarm)
            if rule_result == True and rule.stop == True:
                break

    @classmethod
    def alarm_triggers(cls):
        """
        Returns a list of Triggers that can match alarms
        """
        return DBSession.query(cls).filter(cls.match_type==match_types.index('Alarm'))

    @classmethod
    def event_triggers(cls):
        """
        Returns a list of Triggers that can match events
        """
        return DBSession.query(cls).filter(cls.match_type==match_types.index('Event'))

class TriggerRule(DeclarativeBase):
    """
    A single rule or line of a set for a trigger.
    Using and/or with an action will trigger off only on this
    rule and previous rules in the set.
    The stop field will mean no more rules for this Trigger are evaluated
    if this rule is true.
    """
    __tablename__ = 'trigger_rules'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    trigger_id = Column(Integer, ForeignKey('triggers.id'), nullable=False)
    trigger = relationship('Trigger')
    position = Column(SmallInteger, nullable=False, default=1)
    field = Column(SmallInteger, nullable=False, default=0)
    operator = Column(SmallInteger, nullable=False, default=0)
    value = Column(Unicode(100))
    action_id = Column(Integer, ForeignKey('actions.id'), nullable=False)
    action = relationship('Action')
    stop = Column(Boolean, nullable=False, default=False)
    and_rule = Column(Boolean, nullable=False, default=True)
    #}

    def __init__(self, trigger=None, field=None, operator=None, value=None, position=1):
        self.trigger = trigger
        if field is not None:
            if field not in trigger_fields:
                ValueError('Trigger Field must be:'+','.join(trigger_fields))
            self.field = trigger_fields.index(field)
        if operator is not None:
            if operator not in rule_operators:
                ValueError('Trigger Operator must be: '+','.join(rule_operators))
            self.operator = rule_operators.index(operator)
        self.value = value
        self.position = position

    def process_alarm(self, previous_result, alarm):
        """
        Process this trigger rule against the alarm
        Returns
          rule_result = whether or not the rule matches
        """
        test_value = self._get_alarm_field(alarm)
        if test_value is None:
            return
        test_result = self.test_rule(previous_result, test_value)
        if test_result == True: # Rule fires
            if self.action is not None:
                pass #FIXME trigger the action

    def test_rule(self, previous_result, test_value):

        test_result = self._test_operation(test_value)
        if previous_result is not None:
            if self.and_rule == True:
                test_result = test_result and previous_result
            else:
                test_result = test_result or previous_result
        return test_result

    def _test_operation(self, test_value):
        """
        Return the result if true
        """
        try:
            op_name = rule_operators.index(self.operation)
        except ValueError:
            return False
        if op_name == '=':
            return unicode(test_value) == self.value
        elif op_name == '<>':
            return unicode(test_value) != self.value
        elif op_name == '>=':
            return test_value >= int(self.value)
        elif op_name == '<=':
            return test_value <= int(self.value)
        elif op_name == 'IN':
            return unicode(test_value) in self.value.split(',')
        elif op_name == '!IN':
            return unicode(test_value) not in self.value.split(',')
        elif op_name == 'C':
            return self.value.find(unicode(test_value)) >= 0
        elif op_name == '!C':
            return self.value.find(unicode(test_value)) == -1
        return False


    def _get_alarm_field(self,alarm):
        """
        Extracts the field out of the given item (event or alarm)
        """
        try:
            field_name = trigger_fields[self.field]
        except ValueError:
            return None
        if field_name == 'Hour':
            pass #FIXENE atract data
        if field_name == 'Active':
            return alarm.active
        if field_name == 'Attribute':
            return alarm.attribute_id
        if field_name == 'Attribute Name':
            return alarm.attribute.display_name
        if field_name == 'Attribute Type':
            return alarm.attribute.attribute_type_id
        if field_name == 'Host':
            return alarm.attribute.host_id
        if field_name == 'Type':
            return alarm.event_type_id

class TriggerField(DeclarativeBase):
    __tablename__ = 'trigger_fields'
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    trigger_id = Column(Integer, ForeignKey('triggers.id'), nullable=False)
    trigger = relationship('Trigger', backref='fields')
    action_field_id = Column(Integer, ForeignKey('action_fields.id'), nullable=False)
    action_field = relationship('ActionField')
    value = Column(Unicode(100), nullable=False, default=u'')
    #}
