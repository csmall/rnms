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
import operator

from sqlalchemy import ForeignKey, Column, Table, and_
from sqlalchemy.orm import relationship 
from sqlalchemy.types import Integer, Unicode, SmallInteger, Boolean

from rnms.model import DeclarativeBase, DBSession, metadata
from rnms.lib.genericset import GenericSet

match_types=('alarm', 'event')
trigger_fields=('attribute_type', 'attribute_name', 'hour', 'event_type', 'duration', 'host', 'map', 'client', 'alarm_state')

def oper_in(x,y):
    return unicode(x) in y.split(',')

def oper_notin(x,y):
    return not oper_in(x,y)

def oper_contains(x,y):
    return x.find(unicode(y)) >= 0

def oper_notcontains(x,y):
    return not oper_contains(x,y)

trigger_user_table = Table('trigger_users', metadata,
    Column('trigger_id', Integer, ForeignKey('triggers.id', onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('tg_user.user_id', onupdate="CASCADE", ondelete="CASCADE")),
    Column('active', Boolean, nullable=False, default=True)
    )

class Trigger(DeclarativeBase, GenericSet):
    """
    Triggers are a list of checks or TriggerRules that evaluate against
    an Alarm or Event.  If they match they pass the Atrribute along with
    the Alarm or Event to an Action.
    """
    __tablename__ = 'triggers'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    match_type = Column(SmallInteger)
    email_owner = Column(Boolean, nullable=False, default=False)
    email_users = Column(Boolean, nullable=False, default=True)
    subject = Column(Unicode(100), nullable=False, default=u'')
    body = Column(Unicode(500), nullable=False, default=u'')
    rules = relationship('TriggerRule', order_by='TriggerRule.position')
    users = relationship('User', secondary=trigger_user_table, backref='triggers')
    #}

    def __init__(self, display_name=None, match_type=None):
        self.display_name = display_name
        if match_type is not None:
            if match_type not in match_types:
                raise ValueError('match_type {} must be Event or Alarm'.format(match_type))
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

    @classmethod
    def alarm_triggers(cls):
        """
        Returns a list of Triggers match alarms
        """
        return DBSession.query(cls).filter(cls.match_type==match_types.index('alarm'))

    @classmethod
    def event_triggers(cls):
        """
        Returns a list of Triggers that can match events
        """
        return DBSession.query(cls).filter(cls.match_type==match_types.index('event'))

    def match_type_name(self):
        return match_types[self.match_type]

class TriggerRule(DeclarativeBase):
    """
    A single rule or line of a set for a trigger.
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
    oper = Column(Unicode(5))
    limit = Column(Unicode(100))
    stop = Column(Boolean, nullable=False, default=False)
    and_rule = Column(Boolean, nullable=False, default=True)
    #}

    allowed_opers={
            '=' : operator.eq,
            '<>': operator.ne,
            '>' : operator.gt,
            '<' : operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            'IN': oper_in,
            '!IN': oper_notin,
            'C': oper_contains,
            '!C': oper_notcontains,
            }

    def __init__(self, trigger=None, field=None, oper=None, value=None, position=1):
        self.trigger = trigger
        if field is not None:
            self.set_field(field)
        if operator is not None:
            self.oper = oper
        self.value = value
        self.position = position

    def field_name(self):
        return trigger_fields[self.field]

    def set_field(self, fname):
        """ Set the field using the fieldname """
        if fname not in trigger_fields:
            ValueError('Trigger Field {} not valid.'.format(fname))
        self.field = trigger_fields.index(fname)

    def set_limit(self, limits):
        from rnms.model import EventType
        """ Convert the limits as tags into indexes """
        fname = trigger_fields[self.field]
        if fname == 'event_type':
            self.limit = ','.join([ str(x[0]) for x in DBSession.query(EventType.id).filter(EventType.tag.in_(limits.split(','))) ])
            return
        raise ValueError('Dont have limits for {}'.format(fname))

    def eval(self, previous_result, alarm):
        """
        Process this trigger rule against the alarm
        Returns
          rule_result = whether or not the rule matches
        """
        if previous_result == True and self.and_rule == False:
            return True # True OR whatever is True

        test_value = self._get_alarm_field(alarm)
        if test_value is None:
            return False
        this_result = self.operate(test_value)
        if self.and_rule == True:
            return previous_result and this_result
        else:
            return previous_result or this_result

    def operate(self, test_value):
        """
        Given the alarm or event field, run the operator against our limit
        """
        try:
            x = float(test_value)
            y = float(self.limit)
        except ValueError:
            x = test_value
            y = self.limit
        try:
            this_oper = self.allowed_opers[self.oper]
        except IndexError:
            logger.error('TriggerRule %s:%d has bad oper %s',self.trigger.display_name, self.position, self,oper)
            return False
        else:
            return this_oper(x,y)


    def _get_alarm_field(self,alarm):
        """
        Extracts the field out of the given item (event or alarm)
        """
        if alarm is None:
            return None
        try:
            field_name = trigger_fields[self.field]
        except ValueError:
            return None
        if field_name == 'hour':
            return alarm.start_time.hour
        if field_name == 'attribute':
            return alarm.attribute_id
        if field_name == 'attribute_name':
            return alarm.attribute.display_name
        if field_name == 'attribute_type':
            return alarm.attribute.attribute_type_id
        if field_name == 'host':
            return alarm.attribute.host_id
        if field_name == 'event_type':
            return alarm.event_type_id
        if field_name == 'alarm_state':
            return alarm.alarm_state_id
    

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
