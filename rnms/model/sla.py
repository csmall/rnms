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
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, metadata, DBSession


class Sla(DeclarativeBase):
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
    group = relationship('SlaGroup', backref='sla')
    #}

class SlaGroup(DeclarativeBase):
    __tablename__ = 'sla_groups'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    sla_id = Column(Integer, ForeignKey('slas.id'), nullable=False)
    position = Column(Integer, nullable=False, default=0)
    showable = Column(Boolean, nullable=False, default=False)
    sla_condition_id = Column(Integer, ForeignKey('sla_conditions.id'))
    sla_conditions = relationship('SlaCondition', backref='sla_groups')

class SlaCondition(DeclarativeBase):
    __tablename__ = 'sla_conditions'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(60), nullable=False, unique=True)
    condition = Column(String(250))
    show_info = Column(String(60))
    show_expression = Column(String(250))
    show_unit = Column(String(60))

