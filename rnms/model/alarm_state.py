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

""" Alarm states """
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, metadata, DBSession


class AlarmState(DeclarativeBase):
    __tablename__ = 'alarm_states'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40),nullable=False, unique=True)
    alarm_level = Column(SmallInteger,nullable=False,default=100)
    sound_in = Column(String(40))
    sound_out = Column(String(40))
    internal_state = Column(SmallInteger,nullable=False)
    
    #}
    @classmethod
    def by_name(cls, display_name):
        """ Return the alarm_state with display_name given. """
        return DBSession.query(cls).filter(
                cls.display_name == display_name).first()
