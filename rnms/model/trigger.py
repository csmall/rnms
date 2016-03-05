# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2016 Craig Small <csmall@enc.com.au>
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

from sqlalchemy import ForeignKey, Column, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Unicode, SmallInteger, Boolean

from rnms.model import DeclarativeBase, DBSession, metadata
from rnms.lib.genericset import GenericSet

trigger_fields = ('attribute_type', 'attribute_name', 'hour', 'event_type',
                  'duration', 'host', 'map', 'client', 'event_state')


class MyOperator(object):

    @classmethod
    def in_(cls, x, y):
        """ Return True if x is found in list y """
        return unicode(x) in y.split(',')

    @classmethod
    def notin(cls, x, y):
        """ Return True is x is not found in list y """
        return not cls.in_(x, y)

    @classmethod
    def contains(cls, x, y):
        """ Return true if x is found in string y """
        return y.find(unicode(x)) >= 0

    @classmethod
    def notcontains(cls, x, y):
        """ Return True if x is not found in string y """
        return not cls.contains(x, y)

trigger_user_table = Table(
    'trigger_users', metadata,
    Column('trigger_id', Integer,
           ForeignKey('triggers.id', onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Integer,
           ForeignKey('tg_user.user_id',
                      onupdate="CASCADE", ondelete="CASCADE")),
    Column('active', Boolean, nullable=False, default=True)
    )


class Trigger(DeclarativeBase, GenericSet):
    """
    Triggers are a list of checks or TriggerRules that evaluate against
    an Event.  If they match they pass the Atrribute along with
    the Event to an Action.
    """
    __tablename__ = 'triggers'

    # { Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    email_owner = Column(Boolean, nullable=False, default=False)
    email_users = Column(Boolean, nullable=False, default=True)
    subject = Column(Unicode(100), nullable=False, default=u'')
    body = Column(Unicode(500), nullable=False, default=u'')
    alarmed_only = Column(Boolean, nullable=False, default=True)
    rules = relationship('TriggerRule', order_by='TriggerRule.position')
    users = relationship('User', secondary=trigger_user_table,
                         backref='triggers')
    # }

    def __init__(self, display_name=None):
        self.display_name = display_name
        self.rows = self.rules

    def __repr__(self):
        return '<Trigger name={} rules={}>'.format(
                self.display_name, len(self.rules))

    def insert(self, new_pos, new_row):
        new_row.trigger = self
        GenericSet.insert(self, new_pos, new_row)

    def append(self, new_row):
        new_row.trigger = self
        GenericSet.append(self, new_row)


class TriggerRule(DeclarativeBase):
    """
    A single rule or line of a set for a trigger.
    The stop field will mean no more rules for this Trigger are evaluated
    if this rule is true.
    """
    __tablename__ = 'trigger_rules'

    # { Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    trigger_id = Column(Integer, ForeignKey('triggers.id'), nullable=False)
    trigger = relationship('Trigger')
    position = Column(SmallInteger, nullable=False, default=1)
    field = Column(SmallInteger, nullable=False, default=0)
    oper = Column(Unicode(5))
    limit = Column(Unicode(100))
    stop = Column(Boolean, nullable=False, default=False)
    and_rule = Column(Boolean, nullable=False, default=True)
    # }

    allowed_opers = {
            '=':  operator.eq,
            '<>': operator.ne,
            '>':  operator.gt,
            '<':  operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            'IN': MyOperator.in_,
            '!IN': MyOperator.notin,
            'C': MyOperator.contains,
            '!C': MyOperator.notcontains,
            }

    def __init__(self, trigger=None, field=None, oper=None, value=None,
                 position=1):
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
            self.limit = ','.join(
                [unicode(x[0]) for x in DBSession.query(EventType.id).
                    filter(EventType.tag.in_(limits.split(',')))])
            return
        raise ValueError('Dont have limits for {}'.format(fname))

    def eval(self, previous_result, event):
        """
        Process this trigger rule against the event
        Returns
          rule_result = whether or not the rule matches
        """
        if previous_result and not self.and_rule:
            return True  # True OR whatever is True

        test_value = self._get_event_field(event)
        if test_value is None:
            return False
        this_result = self.operate(test_value)
        if self.and_rule is True:
            return previous_result and this_result
        else:
            return previous_result or this_result

    def operate(self, test_value):
        """
        Given the event field, run the operator against our limit
        """
        try:
            x = float(test_value)
            y = float(self.limit)
        except ValueError:
            x = test_value
            y = self.limit
        try:
            this_oper = self.allowed_opers[self.oper]
        except KeyError:
            return False
        else:
            return this_oper(x, y)

    def _get_event_field(self, event):
        """
        Extracts the field out of the given event
        """
        if event is None:
            return None
        try:
            field_name = trigger_fields[self.field]
        except ValueError:
            return None
        if field_name == 'hour':
            return event.created.hour
        if field_name == 'attribute':
            return event.attribute_id
        if field_name == 'attribute_name':
            return event.attribute.display_name
        if field_name == 'attribute_type':
            return event.attribute.attribute_type_id
        if field_name == 'host':
            return event.attribute.host_id
        if field_name == 'event_type':
            return event.event_type_id
        if field_name == 'event_state':
            return event.event_state_id


class TriggerField(DeclarativeBase):
    __tablename__ = 'trigger_fields'
    # { Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    trigger_id = Column(Integer, ForeignKey('triggers.id'), nullable=False)
    trigger = relationship('Trigger', backref='fields')
    action_field_id = Column(Integer, ForeignKey('action_fields.id'),
                             nullable=False)
    action_field = relationship('ActionField')
    value = Column(Unicode(100), nullable=False, default=u'')
    # }
