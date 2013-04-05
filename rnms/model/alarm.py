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

""" Alarm information """
import datetime

from sqlalchemy import ForeignKey, Column, and_
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Unicode, DateTime, Boolean, String, SmallInteger
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, DBSession
from rnms.lib.states import *

class Alarm(DeclarativeBase):
    """
    An alarm is some sort of alert on an attribute. They are created by
    an Event and share its Severity and EventType.
    If the EventType has a duration then the stop event is the same as the
    start Event and the stop time is after the duration expires.

    Alarms can also be stopped with an UP Event for the same EventType
    and Attribute.

    """
    __tablename__ = 'alarms'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    start_time = Column(DateTime, nullable=False, default=datetime.datetime.now)
    stop_time = Column(DateTime)
    processed = Column(Boolean, nullable=False, default=False)
    attribute_id = Column(Integer, ForeignKey('attributes.id'),nullable=False)
    attribute = relationship('Attribute', backref='alarms')
    alarm_state_id = Column(Integer, ForeignKey('alarm_states.id'),nullable=False)
    alarm_state = relationship('AlarmState')
    event_type_id = Column(Integer, ForeignKey('event_types.id'),nullable=False)
    event_type = relationship('EventType')
    start_event_id = Column(Integer, ForeignKey('events.id'))
    stop_event_id = Column(Integer, ForeignKey('events.id'))
    start_event = relationship("Event",
            primaryjoin="Event.id==Alarm.start_event_id")
    stop_event = relationship("Event",
            primaryjoin="Event.id==Alarm.stop_event_id")
    #}

    def __init__(self,event=None):
        if event is not None:
            self.start_event = event
            self.start_time = event.created
            self.attribute = event.attribute
            self.event_type = event.event_type
            self.alarm_state = event.alarm_state
            if event.event_type.alarm_duration > 0:
                self.stop_time = datetime.datetime.now() + datetime.timedelta(minutes=event.event_type.alarm_duration)
                self.stop_event = event

    def __repr__(self):
        return '<Alarm {0} A:{1} T:{2}>'.format(self.id, self.attribute_id, self.start_time)

    def substitutes(self):
        """
        Returns a dictionary of parameters that are used for replacing
        information.
        """
        subs={'attribute': '', 'client':'', 'host':'', 'state':''}
        if self.attribute is not None:
            subs['attribute'] = self.attribute.display_name
            subs['client'] = self.attribute.user.display_name
            subs['interface-description'] = ' '.join(
                    [af.value for af in self.attribute.fields if af.attribute_type.field.description==True])
            if self.attribute.host:
                subs['host'] = self.attribute.host.display_name
        return subs


    def set_stop(self, stop_event, alarm_state=None):
        """
        Set the stop attributes for this alarm.  
        Requires the event that stopped the alarm and an optional
        new alarm_state to set the alarm to.
        Processed flag is cleared for the consolidator to trigger on
        an up alarm
        """
        if alarm_state is None:
            self.alarm_state = stop_event.alarm_state
        else:
            self.alarm_state = alarm_state
        self.stop_time = stop_event.created
        self.stop_event = stop_event
        self.processed = False

    @classmethod
    def find_down(cls,attribute,event_type):
        """
        Find the first down or testing alarm of the given event_type
        for this attribute.
        """
        if attribute is None or event_type is None:
            return None
        return DBSession.query(cls).filter(and_(
            cls.attribute_id==attribute.id,
            cls.event_type_id==event_type.id,
            cls.alarm_state_id == AlarmState.id,
            AlarmState.internal_state.in_([STATE_DOWN, STATE_TESTING]),
            )).first()

    def process(self):
        """
        Run though all the triggers there are and attempt to fire
        any for this alarm.
        """

        if self.processed == True:
            return
        from rnms.model import Trigger
        
        triggers = Trigger.alarm_triggers()
        for trigger in triggers:
            trigger_result = trigger.process_alarm(self)
        self.attribute.calculate_oper()
        self.processed = True

 

class AlarmState(DeclarativeBase):
    """
    All Alarms have an AlarmState which is the severity of an Alarm.
    The alarm_level is a priority about which Alarms override others,
    smaller the level, the more important it is.
    Internal state should be one of the values from rnms.lib.states
    """

    __tablename__ = 'alarm_states'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40),nullable=False, unique=True)
    alarm_level = Column(SmallInteger,nullable=False,default=100)
    sound_in = Column(String(40))
    sound_out = Column(String(40))
    internal_state = Column(SmallInteger,nullable=False)
    
    #}

    def __repr__(self):
        return '<AlarmState: %s (%s)>' % (self.display_name, self.internal_state)
    @classmethod
    def by_name(cls, display_name):
        """ Return the alarm_state with display_name given. """
        return DBSession.query(cls).filter(
                cls.display_name == display_name).first()

    def is_up(self):
        """
        Returns true if this alarm has internal state of up.
        """
        return (self.internal_state==STATE_UP)

    def is_down(self):
        """
        Returns true if this alarm has internal state of down.
        """
        return (self.internal_state==STATE_DOWN)

    def is_alert(self):
        """
        Returns true if this alarm has internal state of alert.
        """
        return (self.internal_state==STATE_ALERT)

    def is_testing(self):
        """
        Returns true if this alarm has internal state of testing.
        """
        return (self.internal_state==STATE_TESTING)

    def is_downtesting(self):
        """
        Returns true if this alarm has internal state of testing or down.
        """
        return (self.internal_state==STATE_DOWN or
                self.internal_state==STATE_TESTING)
