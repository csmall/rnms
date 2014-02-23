# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012-2014 Craig Small <csmall@enc.com.au>
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
"""
Model for Backend processes

"""

from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode, String

from rnms.model import DeclarativeBase, DBSession


class Backend(DeclarativeBase):
    """
    Poller and SNMP trap backends
    The backend is used for pollers and for trap receivers and generally
    is used to raise events or to set something in the database.

    All backends have the same set of arguments:
        attribute     - Attribute that was polled
        poller_result - Output from the poller. Can be string or
          dictionary but its the same for same backend type.
    Backends should return a string that describes the status. This
    string appears in the logs.
    """
    __tablename__ = 'backends'

    #{ Columns
    id = Column(Integer, primary_key=True, nullable=False)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    command = Column(String(20))
    parameters = Column(String(250))

    def __init__(self, display_name=None, command='', parameters=''):
        self.display_name = display_name
        self.command = command
        self.parameters = parameters

    def __repr__(self):
        return '<Backend name=%s command=%s>'.format(
            self.display_name, self.command)

    @classmethod
    def by_display_name(cls, display_name):
        """ Return Backend with given class name"""
        return DBSession.query(cls).\
            filter(cls.display_name == display_name).first()

    @classmethod
    def default(cls):
        """ Return Bakend that does nothing, the default """
        return DBSession.query(cls).filter(cls.id == 1).first()
