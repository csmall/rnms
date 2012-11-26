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
""" Raw syslog messages module """
import datetime

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, metadata, DBSession


class Syslog(DeclarativeBase):
    __tablename__ = 'sample_model'
    
    #{ Columns
    time_generated = Column(DateTime, nullable=False)
    hostname = Column(String(60), nullable=False)
    message = Column(String(200), nullable=False)
    processed = Column(Boolean, nullable=False, default=False)
    #}

    def __init__(self, hostname, message, gentime=False):
        self.hostname = hostname
        self.message = message
        if gentime is not None:
            time_generated = gentime

