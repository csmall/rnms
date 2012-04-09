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
import time

from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, metadata, DBSession
from rnms.lib import pollers
from rnms.lib.genericset import GenericSet

__all__ = [ 'PollerSet', 'Poller', 'PollerRow']

class Poller(DeclarativeBase):
    __tablename__ = 'pollers'
    
    #{ Columns
    id = Column(Integer, primary_key=True, nullable=False)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    command = Column(String(60), nullable=False, default='none')
    field = Column(String(20))
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

    def run(self, attribute, poller_buffer):
        """ 
        Run the real poller method "_run_BLAH" based upon the command
        field for this poller.
        """
        if self.command is None or self.command=='none':
            return None
        try:
            real_poller = getattr(pollers, "run_"+self.command)
        except AttributeError:
            logging.error("Poller {0} does not exist.".format(self.command))
            return None
        return real_poller(self,attribute,poller_buffer)


class PollerSet(DeclarativeBase, GenericSet):
    __tablename__ = 'poller_sets'

    #{ Columns
    id = Column(Integer, primary_key=True, nullable=False)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    attribute_type = relationship('AttributeType', backref='poller_sets')
    poller_rows = relationship('PollerRow', order_by='PollerRow.position')

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

    def run(self, attribute, poller_buffer):
        """
        Run the actual polling process for this poller row
        Requires the attribute that calls the poller
        Returns True if it worked or False if not
        """
        if self.poller is None or self.backend is None:
            return False
        start_time = time.time()
        poller_result = self.poller.run(attribute, poller_buffer)
        poller_time = int((time.time() - start_time)*1000)
        if poller_output is None:
            return False
        # Stash everything that comes out of the poller into the buffer
        if type(poller_result)==dict:
            for (k,v) in poller_result:
                if k not in poller_buffer:
                    poller_buffer[k]=v
        elif self.poller.field is not None and self.poller.field not in poller_buffer:
            poller_buffer[self.poller.field] = unicode(poller_result)

        start_time = time.time()
        backend_output =  self.backend.run(attribute, poller_result)
        backend_time = int((time.time() - start_time )*1000)
        if backend_output is None:
            return False
        logging.info("H:%d A:%d P:%d %s() -> %s() (Time P:%0.0f B:%0.0f)" % (
            attribute.host_id, attribute.id, self.position, poller, backend,
            poller_time, backend_time))

        return True
        


