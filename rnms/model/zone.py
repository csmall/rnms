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

""" Template of one of the rnms.models"""
from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode, String, Boolean

from rnms.model import DeclarativeBase, DBSession


class Zone(DeclarativeBase):
    __tablename__ = 'zones'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(60), nullable=False, unique=True)
    short_name = Column(Unicode(10), nullable=False, unique=True)
    icon = Column(String(30))
    showable = Column(Boolean,nullable=False, default=True)
    #}

    def __init__(self, display_name=False, short_name=False, icon=False):
        if display_name:
            self.display_name=display_name
        if short_name:
            self.short_name = short_name
        if icon:
            self.icon = icon


    @classmethod
    def by_name(cls, name):
        """ Return the zone whose disply_name is ``name''."""
        return DBSession.query(cls).filter(cls.display_name==name).first()

    @classmethod
    def default(cls):
        """ Return the default Zone. """
        return DBSession.query(cls).order_by('zones.id').first()
