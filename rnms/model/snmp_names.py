# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2013-2015 Craig Small <csmall@enc.com.au>
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
""" Event Handling """

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, and_
from sqlalchemy.types import Integer, Unicode, String 

from rnms.model import DeclarativeBase, DBSession

class SNMPEnterprise(DeclarativeBase):
    """
    Every SNMP enabled device has an Enterprise number. This number can be
    found by polling system.sysObjectID which will return an OID
    1.3.6.1.4.1.X where X is the Enterprise Number
    The device offset is how many digits in the OID to swallow before the
    device ID starts
    
    For example, a Cisco 1720 router has the OID .1.3.6.1.4.1.9.1.201
    where:
      .1.3.6.1.4.1 is systemObjID
      9 is the enterprise (Cisco)
      The offset is 2, meaning we start at the 2nd digit (the 201)
      201 is the device (1720)
    """
    __tablename__ = 'snmp_enterprises'

    #{ Columns
    id = Column(Integer, primary_key=True)
    display_name = Column(Unicode(40), nullable=False)
    device_offset = Column(Integer, nullable=False, default=0)

    def __init__(self,id=None, display_name=None, device_offset=None):
        self.id = id
        self.display_name = display_name
        self.device_offset = device_offset

    @classmethod
    def by_id(cls, ent_id):
        """ Return SNMP Enterprise for given ent_id """
        return DBSession.query(cls).filter(cls.id==ent_id).first()

    @classmethod
    def oid2name(cls, oid):
        """
        Given the filtered systemObjectID minus the 1.3.6.1.4.1
        return the vendor and device name for it
        OID is a string
        Returns: list of 2 strings: vendor,device
        """
        if oid is None or oid == '':
            return ('unknown','')
        if oid[:4] == 'ent.':
            idx = 1
        #    offset = 4
        elif oid[:12] == '1.3.6.1.4.1.':
            idx = 6
        #    offset = 12
        else:
            return ('unknown','')
        oid_nums = oid.split('.')[idx:]

        ent = cls.by_id(int(oid_nums[0]))
        if ent is None:
            return ('unknown vendor {}'.format(oid_nums[0]),'')
        if ent.device_offset > len(oid_nums):
            return (ent.display_name, '')

        device_id = '.'.join(oid_nums[ent.device_offset:])
        device = SNMPDevice.by_id(ent.id, device_id)
        if device is None:
            return (ent.display_name, 'unknown {}'.format(device_id))
        return (ent.display_name, device.display_name)



class SNMPDevice(DeclarativeBase):
    """
    Under the SNMP Enterprise, there can be many devices identified by their
    systemObjectID
    """
    __tablename__ = 'snmp_devices'
    id = Column(Integer, autoincrement=True, primary_key=True)
    oid = Column(String(40), nullable=False)
    enterprise_id = Column(Integer, ForeignKey('snmp_enterprises.id'))
    enterprise = relationship('SNMPEnterprise', backref='devices')
    display_name = Column(Unicode(40), nullable=False)

    def __init__(self, enterprise=None, oid=None, display_name=None):
        self.enterprise = enterprise
        self.oid = oid
        self.display_name = display_name

    @classmethod
    def by_id(cls, ent_id, oid):
        """ Return SNMP Device for given enterpise and given device id """
        return DBSession.query(cls).filter(and_(cls.enterprise_id==ent_id, cls.oid==oid)).first()

