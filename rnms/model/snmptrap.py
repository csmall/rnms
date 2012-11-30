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
""" SNMP Traps model """

from sqlalchemy import ForeignKey, Column, String, Boolean, relationship
from sqlalchemy.types import Integer, Unicode, PickleType, SmallInteger
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, DBSession, Host


class SnmpTrap(DeclarativeBase):
    """
    A raw SNMP trap that has been created by snmptrapd along
    with the varbinds
    """
    __tablename__ = 'snmp_traps'
    
    #{ Columns
    id = Column(Integer, primary_key=True)
    source_address = Column(String(40), nullable=False)
    enterprise = Column(String(250), nullable=False)
    agent_address = Column(String(40), nullable=False)
    trap_oid = Column(String(250), nullable=False)
    processed = Column(Boolean, nullable=False, default=False)
    #}

    def __init__(self, ip, trap_oid):
        self.source_address = ip
        self.agent_address = ip
        self.trap_oid = trap_oid

    def process(self):
        """
        Process this trap, this is done by the consolidator and will create
        a new event, if required
        """
        host = Host.by_address(self.ip)
        if host is None:
            self.processed=1
            return

        trap_matches = DBSession.query(TrapMatches)
        for trap_match in trap_matches:
            match = trap_match.match_oid_sre.match(self.trap_oid)
            if match is not None:
                (matched, receiver_result) = trap_match.run(self, host)
                if matched == True:
                    backend_result = trap_match.backend(attribute, receiver_result)
                    logging.info("T {0} := {1}({3}): -> {4}(): {5}".format(
                        self.id, trap_match.display_name,
                        self.trap_oid, trap_match.backend.display_name,
                        backend_result))
                if trap_match.stop_if_match == True:
                    break
        self.processed=True



class SnmpTrapVarbinds(DeclarativeBase):
    __tablename__ = 'snmp_trap_varbinds'
    
    #{ Columns
    trap_id = Column(Integer, ForeignKey('snmp_traps.id'), nullable=False)
    trap = relationship('SnmpTrap', backref='varbinds')
    oid = Column(String(250), nullable=False)
    value = Column(String(250), nullable=False)
    #}

class TrapMatches(DeclarativeBase):
    __tablename__ = 'trap_matches'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    position = Column(SmallInteger, nullable=False, default=1)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    match_oid_text = Column(Unicode(250), nullable=False, unique=True)
    match_oid_sre = Column(PickleType)
    command = Column(Unicode(40), nullable=False)
    stop_if_match = Column(Boolean, nullable=False, default=True)
    parameters = Column(Unicode(250))
    backend_id = Column(Integer, ForeignKey('backends.id'))
    backend = relationship('Backend')

    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))


    def run(self, host):
        """
        Run the trap matching. The purpose of this method is to 
        further check that the trap matches and to return an attribute.
        """

