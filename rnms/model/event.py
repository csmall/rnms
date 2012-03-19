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

""" Event Handling """
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, Boolean
#from sqlalchemy.orm import relation, backref
import datetime
from string import Template

from rnms.model import DeclarativeBase, metadata, DBSession, Attribute

class EventTextTemplate(Template):
    """ Sub-class of Template to parse the event type strings """
#    pattern = r"""
#     <(?P.*)>  # Replace anything between <>
#     (?P)(?P)(?P)"""
    delimiter = '<'
    pattern = r'''
     <(?:
     (?P<escaped><)|
     (?P<named>[a-z][a-z0-9-]*)>|
     {(?P<braced>[a-z][a-z0-9-]*)}|
     (?P<invalid>)
     )
     '''



class Event(DeclarativeBase):
    """
    An Event is something that has either happened to a host or to an Attribute.
    It may (and probably should) have an AlarmState which is the severity level
    of the event.  Events should only have host or attribute set, never both.
    If both are set, the host will return attribute.host not what you set.
    New Events that are created should have all their values set then use
    the process() method.
    """

    __tablename__ = 'events'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    event_type_id = Column(Integer, ForeignKey('event_types.id'), nullable=False)
    event_type = relationship('EventType')
    host_id = Column(Integer, ForeignKey('hosts.id'))
    host = relationship('Host', backref='events', order_by='Host.id')
    attribute_id = Column(Integer, ForeignKey('attributes.id'))
    attribute = relationship('Attribute', backref='events')
    alarm_state_id = Column(Integer, ForeignKey('alarm_states.id'))
    alarm_state = relationship('AlarmState')
    acknowledged = Column(Boolean, nullable=False, default=False)
    processed = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    fields = relationship('EventField', backref='event', order_by='EventField.tag', cascade='all, delete, delete-orphan')

    def __init__(self, event_type=None, host=None, attribute=None, alarm_state=None, field_list=None):
        self.event_type = event_type
        if attribute is not None:
            self.attribute=attribute
        #elif host is not None:
        #    self.host = host
        self.alarm_state=alarm_state
        if field_list is not None:
            for field_tag in field_list.keys():
                self.fields.append(EventField(field_tag,field_list[field_tag]))

    @classmethod
    def add_admin(cls, host=None, attribute=None, field_list=None):
        event_type = EventType.by_name('Administrative')
        if event_type is not None:
            return Event(event_type=event_type, host=host, attribute=attribute, field_list=field_list)

    def text(self):
        """
        Returns a text string of the event using various sources to fill in
        the blanks. The text template comes from the EventType.text field
        and has fields <likethis> replaced:
          attribute  Attribute.display_name
          attribute-description   All Attribute.fields joined
          client     User.display_name
          host       Host.display_name OR Attribute.host.display_name
          state      AlarmState.display_name
          
          info       event field (from JFFNMS)
          user       event field (from JFFNMS)

          Other fields are just event fields
        """
        text_template = EventTextTemplate(self.event_type.text)
        subs = { 'attribute': '', 'client':'', 'host':'', 'state':'',
                'info':'', 'user':''}
        if self.alarm_state:
            subs['state'] = self.alarm_state.display_name
        if self.attribute is not None:
            subs['attribute'] = self.attribute.display_name
            subs['client'] = self.attribute.user.display_name
            subs['interface-description'] = ' '.join(
                    [af.value for af in self.attribute.fields if af.attribute_type_field.description==True])
            subs['host'] = self.attribute.host.display_name
        elif self.host:
            subs['host'] = self.host.display_name
        subs.update(dict([ef.tag,ef.data] for ef in self.fields))
        return text_template.safe_substitute(subs)

    def process(self):
        """
        Process this event.  This used to be consolidation but it is
        now directly triggered when or near when the event is created.
        """
        if self.processed == True:
            return #done it already

        if self.alarm_state is None:
            logging.warn("Event to be processed but no alarm_state.")
            return
        if self.host is None and self.attribute is None:
            logging.warn("Event to be processed with no attribute or host.")
            return
        if self.event_type is None:
            logging.warn("Event to be procesed with no event_type.")
            return

        if self.attribute is not None:
            if self.alarm_state.is_alert():
                self._process_event_alert()
            else:
                down_alarm = model.Alarm.find_down(self.attribute,self.event_type)
                if self.alarm_state.is_downtesting():
                    self._process_event_downtesting(down_alarm)
                elif self.alarm_state.is_up():
                    self._process_event_up(other_alarm)
        if self.alarm_state.is_up():
            self.acknowledged = True
        self.processed = True

    def _process_event_alert(self):
        """
        Process alert events.  These are unusual as they have a 
        fixed stop time and the stop_event is the start_event.
        Used mainly for Administration and SLA alarms that are
        only around for some time.
        Alert level events must have an attribute to raise an alarm.
        """
        logging.info("E %d := ALERT Attribute %s",
                self.id, self.attribute.display_name)
        new_alarm = model.Alarm(event=self)
        new_alarm.stop_time = datetime.datetime.now() + datetime.timedelta(minutes=(self.event_type.alarm_duration+30))
        new_alarm.stop_event = self
        DBSession.add(new_alarm)

    def _process_event_downtesting(self, other_alarm):
        """
        Process down or testing events
        """
        if other_alarm is not None:
            other_alarm.set_stop(event, alarm_state=model.AlarmState.by_name('up'))
            event.acknowledged=True
            other_alarm.start_event.acknowledged=True

        logging.info("E %d:= DOWN/TESTING Interface %s",
            event.id, event.attribute.display_name)

        new_alarm = model.Alarm(event)
        DBSession.add(new_alarm)

    def _process_event_up(self, other_alarm):
        self.acknowledged=True
        if other_alarm is not None:
            logging.info("E %d:= UP Interface %s",
                self.id, self.attribute.display_name)
            other_alarm.set_stop(self)
            other_alarm.start_event.acknowledged=True



class EventField(DeclarativeBase):
    __tablename__ = 'event_fields'
    
    def __init__(self, new_tag=None, new_data=None):
        if new_tag is not None and new_data is not None:
            self.tag = new_tag
            self.data = new_data
    
    #{ Columns
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False, primary_key=True)
    tag = Column(String(20), nullable=False, primary_key=True)
    data = Column(String(150))
    UniqueConstraint('tag', 'event_id')
    #}

class EventType(DeclarativeBase):
    __tablename__ = 'event_types'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(60), nullable=False, unique=True)
    text = Column(Unicode(250))
    showable = Column(SmallInteger,nullable=False,default=1)
    generate_alarm = Column(Boolean,nullable=False,default=False)
    up_event_id = Column(Integer, ForeignKey('event_types.id'))
    alarm_duration = Column(Integer,nullable=False,default=0)
    show_host = Column(Boolean,nullable=False,default=True)
    severity_id = Column(Integer, ForeignKey('event_severities.id'))
    severity = relationship('EventSeverity', order_by='EventSeverity.id', backref='event_types')
    #}

    def __init__(self, display_name=None):
        if display_name is not None:
            self.display_name=display_name

    def __repr__(self):
        return '<EventType name={0}>'.format(self.display_name)

    @classmethod
    def by_name(cls, name):
        """ Return the Event Type whose display_name is ``name``."""
        return DBSession.query(cls).filter(cls.display_name==name).first()

    @classmethod
    def by_id(cls, event_id):
        """ Return the Event Type whose id is ``event_id``."""
        return DBSession.query(cls).filter(cls.id==event_id).first()

class EventSeverity(DeclarativeBase):
    __tablename__ = 'event_severities'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    level = Column(SmallInteger,nullable=False,default=0)
    bgcolor = Column(String(6), nullable=False)
    fgcolor = Column(String(6), nullable=False)
    #}

    def __init__(self, display_name=None, level=0, bgcolor='ffffff', fgcolor='000000'):
        self.display_name = display_name
        self.level = level
        self.bgcolor = bgcolor
        self.fgcolor = fgcolor

    @classmethod
    def by_name(cls, name):
        """ Return the Event Severity whose display_name is ``name``."""
        return DBSession.query(cls).filter(cls.display_name==name).first()

