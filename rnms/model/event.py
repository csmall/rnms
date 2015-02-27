# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2015 Craig Small <csmall@enc.com.au>
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
""" Event Handling """

import datetime
import logging

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, UniqueConstraint, and_, desc
from sqlalchemy.types import Integer, Unicode, String, Boolean, SmallInteger, DateTime

from rnms.model import DeclarativeBase, DBSession, Attribute
from rnms.lib.parsers import fill_fields
from rnms.lib import states

logger = logging.getLogger('Event')

class Event(DeclarativeBase):
    """
    An Event is something that has either happened to a host or to an Attribute.
    It may (and probably should) have an EventState which is the severity level
    of the event.  Events should only have host or attribute set, never both.
    If both are set, the host will return attribute.host not what you set.

    Alarmed Events
    If the EventType.generate_alarm is set for this Event then on creation
    the alarmed flag is set. 
    Another Event may clear this one if it has an internal state of UP
    and is of same Atribute and Type, this will set stop_time
    A live Alarmed Event is one with alarmed set and stop_time clear.
    """

    __tablename__ = 'events'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    event_type_id = Column(Integer, ForeignKey('event_types.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    event_type = relationship('EventType')
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete="CASCADE", onupdate="CASCADE"))
    host = relationship('Host', backref='events', order_by='Host.id')
    attribute_id = Column(Integer, ForeignKey('attributes.id', ondelete="CASCADE", onupdate="CASCADE"))
    attribute = relationship('Attribute', backref='events')
    event_state_id = Column(Integer, ForeignKey('event_states.id'))
    event_state = relationship('EventState')
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    stop_time = Column(DateTime)
    alarmed = Column(Boolean, nullable=False, default=False)
    acknowledged = Column(Boolean, nullable=False, default=False)
    processed = Column(Boolean, nullable=False, default=False)
    triggered = Column(Boolean, nullable=False, default=False)
    check_stop_time = Column(Boolean, nullable=False, default=False)
    fields = relationship('EventField', backref='event', order_by='EventField.tag', cascade='all,delete,delete-orphan')

    def __init__(self, event_type, host=None, attribute=None, event_state=None, field_list=None):
        self.event_type = event_type
        if attribute is not None:
            self.attribute=attribute
            self.host = attribute.host
            if event_type.generate_alarm == True:
                self.alarmed = True
                if event_type.alarm_duration > 0:
                    self.check_stop_time = True
        elif host is not None:
            self.host = host
        self.event_state=event_state
        if field_list is not None:
            for field_tag in field_list.keys():
                self.fields.append(EventField(field_tag,field_list[field_tag]))

    @classmethod
    def create_sla(cls, attribute, info, details):
        """
        Create and return a new Event that is of a SLA type
        Parameters:
          attribute - The attribe the SLA event is for
          info - sla row event_text
          details - other details of the event
        """
        event_type = EventType.by_tag('sla')
        event_state = EventState.by_name('alert')
        if event_type is None or event_state is None:
            return None
        event_fields={ 'info': info, 'details': details}
        return Event(event_type=event_type, attribute=attribute, field_list=event_fields, event_state=event_state)

    @classmethod
    def create_admin(cls, host=None, attribute=None, info=None):
        """
        Create and return a new administrative event.
        Parameters:
          host: optional host object
          attribute: optional attribute object
          info: string of additional information
        """

        if info is None:
            field_list = None
        else:
            field_list = {'info': info}
        event_type = EventType.by_tag('admin')
        if event_type is not None:
            return Event(event_type=event_type, host=host, attribute=attribute, field_list=field_list, event_state=EventState.by_name('alert'))
        return None

    @classmethod
    def alarmed_events(cls, conditions):
        """
        Find all alarmed Events with extra conditions
        """
        conditions.extend([
            cls.alarmed == True,
            cls.stop_time == None,])
        return DBSession.query(cls).join(EventState).filter(and_(*conditions))

    @classmethod
    def check_time_events(cls):
        """
        Return a list of all alarmed Events that need the stop_time checked
        """
        return cls.alarmed_events(
            [cls.check_stop_time == True,
             cls.stop_time < datetime.datetime.now()])

    @classmethod
    def find_down(cls, attribute_id, event_type_id, exclude_event=None):
        """
        Find the first down or testing alarmed Event of the given
        EventType and Attribute
        """
        conditions = [
            cls.alarmed == True,
            cls.stop_time == None,
            cls.attribute_id == attribute_id,
            cls.event_type_id == event_type_id,
            EventState.internal_state.in_(
                [states.STATE_DOWN, states.STATE_TESTING])
        ]
        if exclude_event is not None:
            conditions.append(cls.id != exclude_event)
        return DBSession.query(cls).join(EventState).filter(
            and_(*conditions)).order_by(desc(cls.id)).first()

    @classmethod
    def attribute_alarm(cls, attribute_id):
        """
        Return the highest priority alarmed Event for the given Attribute id
        """
        return cls.alarmed_events(
            [cls.attribute_id == attribute_id]).order_by(
            desc(EventState.priority)).first()

    @classmethod
    def host_alarm(cls, host_id):
        """
        Return the highest priority alarmed Event for the given Host id
    """
        return cls.alarmed_events(
            [cls.attribute_id.in_(
                DBSession.query(Attribute.id).\
                filter(Attribute.host_id == host_id))]).order_by(
                desc(EventState.priority)).first()



    def text(self):
        """
        Returns a text string of the event using various sources to fill in
        the blanks. The text template comes from the EventType.text field
        and has fields <likethis> replaced:
          attribute  Attribute.display_name
          attribute-description   Attribute.description
          client     User.display_name
          host       Host.display_name OR Attribute.host.display_name
          state      EventState.display_name

          info       event field (from JFFNMS)
          user       event field (from JFFNMS)

          Other fields are just event fields
        """
        return fill_fields(self.event_type.text, host=self.host, attribute=self.attribute, event=self) 

    def set_processed(self):
        self.processed = True

    def set_stop(self, stop_event):
        """
        Stop this alarmed Event
        """
        self.stop_time = stop_event.created
        self.check_stop_time = False
        self.acknowledged = True


class EventField(DeclarativeBase):
    __tablename__ = 'event_fields'

    def __init__(self, new_tag=None, new_data=None):
        if new_tag is not None and new_data is not None:
            self.tag = new_tag
            self.data = new_data

    #{ Columns
    event_id = Column(Integer, ForeignKey('events.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=False, primary_key=True)
    tag = Column(String(20), nullable=False, primary_key=True)
    data = Column(String(150))
    UniqueConstraint('tag', 'event_id')
    #}

class EventType(DeclarativeBase):
    __tablename__ = 'event_types'

    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(60), nullable=False, unique=True)
    tag = Column(String(40), unique=True)
    text = Column(Unicode(250))
    showable = Column(SmallInteger,nullable=False,default=1)
    generate_alarm = Column(Boolean,nullable=False,default=False)
    alarm_duration = Column(Integer,nullable=False,default=0)
    show_host = Column(Boolean,nullable=False,default=True)
    #}

    def __init__(self, display_name=None):
        if display_name is not None:
            self.display_name=display_name

    def __repr__(self):
        return '<EventType name={0}>'.format(self.display_name)

    @classmethod
    def by_tag(cls, tag):
        """ Return the Event Type with the given tag """
        return DBSession.query(cls).filter(cls.tag==tag).first()

    @classmethod
    def by_name(cls, name):
        """ Return the Event Type with the given display_name """
        return DBSession.query(cls).filter(cls.display_name==name).first()

    @classmethod
    def by_id(cls, event_id):
        """ Return the Event Type whose id is ``event_id``."""
        return DBSession.query(cls).filter(cls.id==event_id).first()

class Severity(DeclarativeBase):
    __tablename__ = 'severities'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    bgcolor = Column(String(6), nullable=False, default='ffffff')
    fgcolor = Column(String(6), nullable=False, default ='ffffff')
    #}

    def __init__(self, display_name=None, bgcolor='ffffff', fgcolor='000000'):
        self.display_name = display_name
        self.bgcolor = bgcolor
        self.fgcolor = fgcolor

    @classmethod
    def by_name(cls, name):
        """ Return the Severity whose display_name is ``name``."""
        return DBSession.query(cls).filter(cls.display_name==name).first()

class EventState(DeclarativeBase):
    """
    All Events and Alarms have an EventState which is the severity 
    of the object. 
    The priority is a number between 0-100 where the lowest number is
    the more important Event or Alarm
    Internal state should be one of the values from rnms.lib.states
    """

    __tablename__ = 'event_states'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40),nullable=False, unique=True)
    priority = Column(SmallInteger,nullable=False,default=100)
    sound_in = Column(String(40))
    sound_out = Column(String(40))
    internal_state = Column(SmallInteger,nullable=False)
    severity_id = Column(Integer, ForeignKey('severities.id'), nullable=False )
    severity = relationship('Severity')

    #}

    def __repr__(self):
        return '<EventState: %s (%s)>' % (self.display_name, self.internal_state)

    @classmethod
    def by_name(cls, display_name):
        """ Return the event_state with display_name given. """
        return DBSession.query(cls).filter(
                cls.display_name == display_name).first()

    @classmethod
    def get_up(self):
        """ Reutrn the event_state that is for Up """
        return self.by_name(u'up')

    def is_up(self):
        """
        Returns true if this alarm has internal state of up.
        """
        return (self.internal_state==states.STATE_UP)

    def is_down(self):
        """
        Returns true if this alarm has internal state of down.
        """
        return (self.internal_state== states.STATE_DOWN)

    def is_alert(self):
        """
        Returns true if this alarm has internal state of alert.
        """
        return (self.internal_state== states.STATE_ALERT)

    def is_testing(self):
        """
        Returns true if this alarm has internal state of testing.
        """
        return (self.internal_state== states.STATE_TESTING)

    def is_downtesting(self):
        """
        Returns true if this alarm has internal state of testing or down.
        """
        return (self.internal_state== states.STATE_DOWN or
                self.internal_state== states.STATE_TESTING)
