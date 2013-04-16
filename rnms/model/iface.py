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
""" Physical and Logical Interface model """

from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, String, Unicode

from rnms.model import DeclarativeBase


class Iface(DeclarativeBase):
    __tablename__ = 'interfaces'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete="CASCADE", onupdate="CASCADE"))
    ifindex = Column(Integer, nullable=False) #ifIndex
    display_name = Column(Unicode(30)) #ifDescr or idXName
    iftype = Column(Integer, nullable=False,default=1) # other
    speed = Column(Integer)
    physaddr = Column(String(30)) #MAC address usually
    stacklower = Column(Integer, nullable=False,default=0) # ifStackLowerLayer
    #}
