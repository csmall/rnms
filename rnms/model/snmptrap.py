# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2015 Craig Small <csmall@enc.com.au>
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
""" SNMP Traps model """
import re

from sqlalchemy import ForeignKey, Column, String, Boolean
from sqlalchemy.types import Integer, Unicode, SmallInteger
from sqlalchemy.orm import relationship

from rnms.model import DeclarativeBase, DBSession


OID_RE = re.compile('^(?:\d+\.)\d+$')
SNMP_UPTIME = '1.3.6.1.2.1.1.3.0'


class SnmpTrap(DeclarativeBase):
    """
    A raw SNMP trap that has been created by snmptrapd along
    with the varbinds. The trapd checks the incoming packet is
    from a known host and converts v1 packets to v2c format
    """
    __tablename__ = 'snmp_traps'

    #{ Columns
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer,
                     ForeignKey('hosts.id', ondelete="CASCADE",
                                onupdate="CASCADE"))
    varbinds = relationship('SnmpTrapVarbind', backref='trap')
    trap_oid = Column(String(250), nullable=False)
    processed = Column(Boolean, nullable=False, default=False)
    #}

    def __init__(self, host_id=None, trap_oid=None):
        if host_id is not None:
            self.host_id = host_id
        if trap_oid is not None:
            self.trap_oid = trap_oid

    def __repr__(self):
        if self.host:
            host_id = self.host.id
        else:
            host_id = 'none'
        return '<SNMP Trap host={} varbinds={}>'.\
            format(host_id, len(self.varbinds))

    def set_uptime(self, uptime):
        """ Set the uptime VarBind for this trap """
        self.set_varbind(SNMP_UPTIME, uptime)

    def set_varbind(self, name, value):
        """ Add a varbind to this trap """
        self.varbinds.append(SnmpTrapVarbind(name, value))

    def get_varbind(self, oid, default=None):
        """ Return the value of the given OID for the VarBind """
        for varbind in self.varbinds:
            if varbind.oid == oid:
                return varbind.value
        return default


class SnmpTrapVarbind(DeclarativeBase):
    __tablename__ = 'snmp_trap_varbinds'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    trap_id = Column(Integer,
                     ForeignKey('snmp_traps.id', ondelete="CASCADE",
                                onupdate="CASCADE"), nullable=False)
    oid = Column(String(250), nullable=False)
    value = Column(String(250), nullable=False)
    #}

    def __init__(self, oid=None, value=None):
        if oid is not None:
            self.oid = oid
        if value is not None:
            self.value = value

    def __repr__(self):
        return '<SNMP VarBind: {}={}>'.format(
            self.oid, self.value)


class TrapMatch(DeclarativeBase):
    __tablename__ = 'trap_matches'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    position = Column(SmallInteger, nullable=False, default=1)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    trap_oid = Column(Unicode(250), nullable=False, unique=True)
    attribute_command = Column(Unicode(40), nullable=False)
    attribute_parameters = Column(Unicode(250))
    stop_if_match = Column(Boolean, nullable=False, default=True)
    backend_id = Column(Integer, ForeignKey('backends.id'))
    backend = relationship('Backend')

    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    attribute_type = relationship('AttributeType')

    @classmethod
    def by_oid(cls, trap_oid):
        """ Return all the TrapMatches that are for the given trap OID
        """
        return DBSession.query(cls).\
            filter(cls.trap_oid == trap_oid).order_by(cls.position)


class TrapMatchValue(DeclarativeBase):
    __tablename__ = 'trap_match_values'

    #{ Columns
    trap_match_id = Column(Integer, ForeignKey('trap_matches.id'),
                           nullable=False, primary_key=True)
    trap_match = relationship('TrapMatch', backref='values')
    key = Column(Unicode(40), nullable=False, primary_key=True)
    command = Column(Unicode(40), nullable=False)
    parameters = Column(Unicode(250))
    #}
