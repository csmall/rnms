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

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, ForeignKeyConstraint
from sqlalchemy.types import Integer, Unicode, String, SmallInteger
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, DBSession
from rnms.lib import pollers
from rnms.lib.genericset import GenericSet
from rnms.lib.parsers import safe_substitute, find_field_keys

__all__ = [ 'PollerSet', 'Poller', 'PollerRow']

class Poller(DeclarativeBase):
    __tablename__ = 'pollers'

    #{ Columns
    id = Column(Integer, primary_key=True, nullable=False)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    command = Column(String(60), nullable=False, default='none')
    field = Column(String(80))
    parameters = Column(String(250), nullable=False, default='')

    def __init__(self,display_name=None, command='none', tag='', parameters=''):
        self.display_name = display_name
        self.command = command
        self.tag = tag
        self.parameters = parameters

    def __repr__(self):
        return '<Poller name=%s plugin=%s>' % (self.display_name, self.plugin_name)
    def __unicode__(self):
        return self.display_name

    @classmethod
    def by_display_name(cls, display_name):
        """ Return Poller with given display_name """
        if display_name is None:
            return None
        return DBSession.query(cls).filter(cls.display_name == display_name).first()

    def run(self, poller_row, pobj, patt, poller_buf):
        """ 
        Run the real poller method "poll_BLAH" based upon the command
        field for this poller.
        """
        if self.command is None or self.command=='none':
            return None
        try:
            real_poller = getattr(pollers, "poll_"+self.command)
        except AttributeError:
            pobj.logger.error(
                "A:%d - Poller function poll_%s does not exist.",
                patt.id, self.command)
            return None
        return real_poller(poller_buf, pobj=pobj, poller_row=poller_row,
                           attribute=patt,
                           parsed_params=self.parsed_parameters(patt))

    def parsed_parameters(self, patt):
        """
        Poller.parameters may have certain fields that need to be parsed
        by filling in <item> with some value from the attribute
        """
        from rnms.model import AttributeField
        if self.parameters == '':
            return ''
        field_keys = find_field_keys(self.parameters)
        if field_keys == []:
            return self.parameters

        # Put in the easy ones
        field_values = {
            'attribute_id': patt.id,
            'host_id': patt.host_id,
            'index': patt.index,
        }
        for field_key in field_keys:
            if field_key in field_values:
                continue
            field_value = AttributeField.field_value(patt.id, field_key)
            if field_value is not None:
                field_values[field_key] = field_value
        return safe_substitute(self.parameters, field_values)


class PollerSet(DeclarativeBase, GenericSet):
    __tablename__ = 'poller_sets'

    #{ Columns
    id = Column(Integer, primary_key=True, nullable=False)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'), nullable=False, default=0)
    attribute_type = relationship('AttributeType', backref='poller_sets', primaryjoin='PollerSet.attribute_type_id == AttributeType.id')
    poller_rows = relationship('PollerRow', order_by='PollerRow.position')
    ForeignKeyConstraint(['attribute_type_id',], ['attribute_types.id',], use_alter=True, name='fk_poller_set_attribute_type_id')

    def __init__(self, display_name=None):
        self.display_name = display_name
        self.rows = self.poller_rows

    def __repr__(self):
        return '<PollerSet name=%s rows=%d>' % (self.display_name,len(self.poller_rows))

    def insert(self, new_pos, new_row):
        new_row.poller_set = self
        GenericSet.insert(self,new_pos, new_row)

    def append(self, new_row):
        new_row.poller_set = self
        GenericSet.append(self,new_row)

    @classmethod
    def no_polling(cls):
        return DBSession.query(cls).order_by(id).first()
    
    @classmethod
    def by_id(cls,pset_id):
        return DBSession.query(cls).filter(cls.id == pset_id).first()

    @classmethod
    def by_display_name(cls,display_name):
        """ Return the PollerSet with the given display name """
        return DBSession.query(cls).filter(cls.display_name == display_name).first()

    def run(self, attribute):
        """
        Run all of the PollerRows within this PollerSet for the
        given attribute.  A buffer is kept between each rows and
        may contain data out of each poller
        """
        poller_buffer={}
        for row in self.poller_rows:
            row.run(attribute, poller_buffer)


class PollerRow(DeclarativeBase):
    __tablename__ = 'poller_rows'
    
    #{ Columns
    poller_set_id = Column(Integer, ForeignKey('poller_sets.id'), primary_key=True, nullable=False)
    poller_set = relationship('PollerSet')
    position = Column(SmallInteger, nullable=False, default=1, primary_key=True)
    poller_id = Column(Integer,  ForeignKey('pollers.id'), nullable=False, default=1)
    poller = relationship('Poller', lazy='joined')
    backend_id = Column(Integer, ForeignKey('backends.id'), nullable=False, default=1)
    backend = relationship('Backend', lazy='joined')
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

    def run_poller(self, pobj, patt, poller_buff):
        """
        Run the actual polling process for this poller row
        Requires the attribute that calls the poller
        Returns True if it worked or False if not
        """
        if self.poller is None:
            pobj.logger.warning('A%d: run_poller called with no poller!',
                               patt.id)
            return False
        if self.poller.id == 1:
            #self.run_backend(patt, None)
            return True
        return self.poller.run(self, pobj, patt, poller_buff)

    def run_backend(self, attribute, value):
        """
        Run the actual backend process for this poller row
        Requires the attribute that calls the poller
        Returns True if it worked or False if not
        """
        if self.backend is None or self.backend.id == 1:
            return ''
        return self.backend.run(self, attribute, value)


