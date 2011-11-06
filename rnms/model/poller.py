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
#
"""Poller model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, metadata, DBSession

__all__ = [ 'PollerSet', 'Poller', 'Backend', 'PollerRow']

class Poller(DeclarativeBase):
    __tablename__ = 'pollers'
    
    #{ Columns
    id = Column(Integer, primary_key=True, nullable=False)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    plugin_name = Column(String(60), nullable=False, default='none')
    tag = Column(String(20))
    parameters = Column(String(250), nullable=False, default='')

    def __init__(self,display_name=None, plugin_name='none', tag='', parameters=''):
        self.display_name = display_name
        self.plugin_name = plugin_name
        self.tag = tag
        self.parameters = parameters

    def __repr__(self):
        return '<Poller name=%s plugin=%s>' % (self.display_name, self.plugin_name)
    def __unicode__(self):
        return self.display_name

class Backend(DeclarativeBase):
    __tablename__ = 'backends'
    
    #{ Columns
    id = Column(Integer, primary_key=True, nullable=False)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    plugin_name = Column(String(60), nullable=False)
    tag = Column(String(20))
    parameters = Column(String(250), nullable=False)

    def __init__(self,display_name=None, plugin_name='none', tag='', parameters=''):
        self.display_name = display_name
        self.plugin_name = plugin_name
        self.tag = tag
        self.parameters = parameters

    def __repr__(self):
        return '<Backend name=%s plugin=%s>' % (self.display_name, self.plugin_name)
    def __unicode__(self):
        return self.display_name

class PollerSet(DeclarativeBase):
    __tablename__ = 'poller_sets'

    #{ Columns
    id = Column(Integer, primary_key=True, nullable=False)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    attribute_type = relationship('AttributeType', backref='poller_sets')
    poller_rows = relationship('PollerRow', order_by='PollerRow.position')

    def __init__(self, display_name=None):
        self.display_name = display_name

    def __repr__(self):
        return '<PollerSet name=%s rows=%d>' % (self.display_name,len(self.poller_rows))

    @classmethod
    def no_polling(cls):
        return DBSession.query(cls).order_by(id).first()
    
    def insert_first(self, new_row):
        """ Add new PollerRow to PollerSet at the top of the set"""
        for row in self.poller_rows:
            if new_row is not row:
                row.position=row.position+1
        new_row.position=1
        new_row.poller_set = self
        self.poller_rows.insert(0,new_row)

    def insert_last(self, new_row):
        """ Add new PollerRow to PollerSet at the bottom of the Set"""
        new_position=1
        for row in self.poller_rows:
            if new_row is not row:
                new_position=row.position+1
        new_row.position=new_position
        new_row.poller_set = self
        self.poller_rows.append(new_row)


    def row_to(self, moving_row, position):
        """
        Move existing PollerRow in PollerSet to be at new position in Set.
        Renumbers subsequent PolleRow positions down one.
        Does not add PollerRow to set, assume its already there.
        """
        for row in self.poller_rows:
            if moving_row is not row and row.position >= position:
                row.position=row.position+1
        moving_row.position=position

    def row_swap(self, position_a, position_b):
        """ Swap position of rows that are the specified positions. If the
        positions don't exist then dont do anything
        """
        for row_a in self.poller_rows:
            if row_a.position == position_a:
                for row_b in self.poller_rows:
                    if row_b.position == position_b:
                        row_a.position = position_b
                        row_b.position = position_a
                        return True
        return False

class PollerRow(DeclarativeBase):
    __tablename__ = 'poller_rows'
    
    #{ Columns
    poller_set_id = Column(Integer, ForeignKey('poller_sets.id'), primary_key=True, nullable=False)
    poller_set = relationship('PollerSet')
    position = Column(SmallInteger, nullable=False, default=1, primary_key=True)
    poller_id = Column(Integer,  ForeignKey('pollers.id'))
    poller = relationship('Poller')
    backend_id = Column(Integer, ForeignKey('backends.id'))
    backend = relationship('Backend')
    #}

    def __init__(self, poller_set=None, poller=None, backend=None, position=1):
        self.poller_set = poller_set
        self.poller = poller
        self.backend = backend
        self.position = position
    
    def __repr__(self):
        if self.poller is not None:
            poller_name = self.poller.display_name
        else:
            poller_name = 'None'
        if self.backend is not None:
            backend_name = self.backend.display_name
        else:
            backend_name = 'None'
        return '<PollerRow position=%d poller=%s backend=%s>' % (self.position, poller_name, backend_name)
