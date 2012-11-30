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
#
"""Sample model module."""

from sqlalchemy import ForeignKey, Column, relationship
from sqlalchemy.types import Integer, Unicode, String, SmallInteger
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase
from rnms.lib.genericset import GenericSet


class Layout(DeclarativeBase):
    __tablename__ = 'layouts'
    
    #{ Columns
    id = Column(Integer, primary_key=True)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    url_slug = Column(String(40), nullable=False, unique=True)
    cols = Column(Integer, nullable=False, default=0)
    #}

class PortletRow(DeclarativeBase, GenericSet):
    __tablename__ = 'portlet_rows'

    #{ Columns
    layout_id = Column(Integer, ForeignKey('layouts.id'), nullable=False)
    layout = relationship('Layout')
    position = Column(SmallInteger, nullable=False, default=1)
    portlet_id = Column(Integer, ForeignKey('portlets.id'))

class Portlets(DeclarativeBase):
    __tablename__ = 'portlets'

    #{ Columns
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(40), nullable=False, unique=True)
    widget_type = Column(String(40), nullable=False)
    widget_params = Column(String(200))
    #}
