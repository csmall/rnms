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
""" SNMP Traps model """
import re

from sqlalchemy import ForeignKey, Column, String, Boolean, and_
from sqlalchemy.types import Integer, Unicode, SmallInteger
from sqlalchemy.orm import relationship

from rnms.model import DeclarativeBase, DBSession, Attribute


OID_RE = re.compile('^(?:\d+\.)\d+$')


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


class TrapMatches(DeclarativeBase):
    __tablename__ = 'trap_matches'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    position = Column(SmallInteger, nullable=False, default=1)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    trap_oid = Column(Unicode(250), nullable=False, unique=True)
    attribute_command = Column(Unicode(40), nullable=False)
    attribute_parameters = Column(Unicode(250))
    value_command = Column(Unicode(40), nullable=False)
    value_parameters = Column(Unicode(250))
    stop_if_match = Column(Boolean, nullable=False, default=True)
    backend_id = Column(Integer, ForeignKey('backends.id'))
    backend = relationship('Backend')

    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    attributetype = relationship('AttributeType')

    @classmethod
    def by_oid(cls, trap_oid):
        """ Return all the TrapMatches that are for the given trap OID
        """
        return DBSession.query(cls).filter(cls.trap_oid == trap_oid).order_by(cls.position)

    def run(self, host, trap):
        """
        Further matching of the trap.  At this point the consolidator
        has found a host that matches the agent's address and a trap_oid
        for this match.

        This method looks at the trap varbinds and attempts to locate
        an attribute of the host plus some optional results.
        The attribute and results will be fed into a backend.
        Returns:
          (attribute, result, error)
            attribute is a matched attribute for this trap. If returns
            None it means there is no match
            result is similiar to a poller result
        """
        if self.attribute_command is None or self.attribute_command=='none' or self.attribute_command=='':
            return (None, None, None)
        if self.value_command is None or self.value_command=='none' or self.value_command=='':
            return (None, None, None)
        
        try:
            real_attribute_command = getattr(self, "_run_attribute_"+self.attribute_command)
        except AttributeError:
            return (None, None, 'attribute command _run_attribute_{} doesnt exist'.format(self.attribute_command))
        
        try:
            real_value_command = getattr(self, "_run_value_"+self.value_command)
        except AttributeError:
            return (None, None, 'attribute command _run_value_{} doesnt exist'.format(self.value_command))

        attribute, error = real_attribute_command(host, trap)
        if error is not None:
            return (None, None, error)
        elif attribute is None:
            return (None, None, None)

        value,error = real_value_command(host, trap)
        if error is not None:
            return (None, None, error)
        return (attribute, value, None)


    ### Real run commands go here
    def _run_attribute_match_index(self, host, trap):
        """
        Match the ID of one of the VarBinds to an Attribute's index field
        and pass back the state. The only Attributes searched in the host
        must have the same AttributeID as the Trap.

        Parameters: <index_oid>
          index_oid = The OID of the VarBind that holds the index
        """
        for varbind in trap.varbinds:
            if varbind.oid == self.attribute_parameters:
                return (DBSession.query(Attribute).filter(and_(
                    Attribute.host_id == host.id,
                    Attribute.attribute_type_id == self.attribute_type_id,
                    Attribute.index == varbind.value
                    )).first(), None)
        return (None,None)

    def _run_attribute_first(self, host, trap):
        """
        Return the first Attribute for given host that has the
        required AttributeType. Used for where the Attribute doesn't
        matter OR there is only one of this AttributeType per host.
        Parameters: ignored
        """
        return (DBSession.query(Attribute).filter(and_(
            Attribute.host_id == host.id,
            Attribute.attribute_type_id == self.attribute_type_id,
            )).first(), None)
        return (None,None)

    def _run_value_oid(self, host, trap):
        """
        Parameters: <oid>|<val1>=<ret1>,...|<default ret>
          oid   = The OID of varbind holding the state
          <val> = Mapping of OID result. If <state> is <val1> then return
                  <ret1> - optional
          <default ret> If state is OID no match of previous field - otional
        """
        params = self.parmeters('|')

        state_oid = params[0]

        for varbind in trap.varbinds:
            if varbind.oid == state_oid:
                if len(params) == 1:
                    return (varbind.value, None)
                
                for item in params[1].split(','):
                    try:
                        (match,ret) = item.split('=')
                    except ValueError:
                        pass
                    else:
                        if varbind.value == match:
                            return (ret, None)
                else:
                    try:
                        return (params[2], None)
                    except IndexError:
                        pass
        return (None, None)

    def _run_value_fixed(self, host, trap):
        """ The value is fixed in the parameters """
        return (self.value_parameters, None)
