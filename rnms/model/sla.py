# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011-2014 Craig Small <csmall@enc.com.au>
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

import logging

from sqlalchemy.orm import relationship, backref
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, SmallInteger
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, DBSession
from rnms.lib.genericset import GenericSet

logger = logging.getLogger('rnms')


class Sla(DeclarativeBase, GenericSet):
    __tablename__ = 'slas'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    display_name = Column(Unicode(60), nullable=False, unique=True)
    event_text = Column(Unicode(60))
    threshold = Column(SmallInteger)
    sla_rows = relationship('SlaRow',
                            backref=backref('sla', lazy='joined'),
                            order_by='SlaRow.position')
    #}

    def __init__(self, display_name=None):
        if display_name is not None:
            self.display_name = display_name
        self.rows = self.sla_rows

    @classmethod
    def by_display_name(cls, name):
        """ Return the SLA with the given display_name """
        return DBSession.query(cls).filter(cls.display_name == name).first()

    def insert(self, new_pos, new_row):
        new_row.sla = self
        GenericSet.insert(self, new_pos, new_row)

    def append(self, new_row):
        new_row.sla = self
        GenericSet.append(self, new_row)


class SlaRow(DeclarativeBase):
    """
    A single row for a SLA that uses a specific SlaCondition
    """
    __tablename__ = 'sla_rows'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    sla_id = Column(Integer,
                    ForeignKey('slas.id', ondelete='CASCADE',
                               onupdate='CASCADE'), nullable=False)
    position = Column(Integer, nullable=False, default=1)
    expression = Column(String(250))
    oper = Column(Unicode(5))
    limit = Column(Integer)
    show_info = Column(Unicode(60))
    show_expression = Column(Unicode(250))
    show_unit = Column(Unicode(60))

    def __init__(self, sla=None, position=1):
        self.sla = sla
        self.position = position

    def __repr__(self):
        if self.sla is not None:
            sla_name = self.sla.display_name
        else:
            sla_name = 'None'
        return '<SlaRow position={} sla={}>'.format(self.position, sla_name)
