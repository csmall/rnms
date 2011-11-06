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
    __tablename__ = 'events'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    event_type_id = Column(Integer, ForeignKey('event_types.id'), nullable=False)
    event_type = relationship('EventType')
    host_id = Column(Integer, ForeignKey('hosts.id'))
    host = relationship('Host', backref='events', order_by='Host.id')
    attribute_id = Column(Integer, ForeignKey('attributes.id'))
    attribute = relationship('Attribute', backref='events')
    state = Column(Unicode(40))
    acknowledged = Column(Boolean, nullable=False, default=False)
    analyzed = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    fields = relationship('EventField', backref='event', order_by='EventField.tag')

    def __init__(self, event_type=None, host=None, attribute=None, field_list=None):
        self.event_type = event_type
        self.host = host
        self.attribute=attribute
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
          host       Host.display_name
          state      Event.state
          
          info       event field (from JFFNMS)
          user       event field (from JFFNMS)
        """
        text_template = EventTextTemplate(self.event_type.text)
        subs = { 'attribute': '', 'client':'', 'host':'', 'state':self.state,
                'info':'', 'user':''}
        if self.host:
            subs['host'] = self.host.display_name
        if self.attribute_id > 1: #FIXME this should be available
            attribute = Attribute.by_id(self.attribute_id)
            if attribute is None:
                print "Cannot find attribute %d" % self.attribute_id
            else:
                subs['attribute'] = attribute.display_name
                subs['client'] = attribute.user.display_name
                subs['interface-description'] = ' '.join(
                        [af.value for af in attribute.fields if af.attribute_type_field.description==True])
        subs.update(dict([ef.tag,ef.data] for ef in self.fields))
        return text_template.safe_substitute(subs)

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
    alarm_duration = Column(Integer)
    show_host = Column(Boolean,nullable=False,default=True)
    severity_id = Column(Integer, ForeignKey('event_severities.id'))
    severity = relationship('EventSeverity', order_by='EventSeverity.id', backref='event_types')
    #}

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

