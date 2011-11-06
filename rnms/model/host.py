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
""" Host definition model """

import datetime
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, Boolean, PickleType, String

from rnms.model import DeclarativeBase, metadata, DBSession
from rnms.lib import snmp

__all__ = ['Host', 'Iface', 'ConfigTransfer', 'HostConfig']

class Host(DeclarativeBase):
    __tablename__ = 'hosts'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    mgmt_address = Column(String(40))
    display_name = Column(String(255), nullable=False)
    community_ro = Column(PickleType)
    community_rw = Column(PickleType)
    zone_id = Column(Integer, ForeignKey('zones.id'))
    zone = relationship('Zone', backref='hosts')
    tftp_server = Column(String(40))
    autodiscovery_policy_id = Column(Integer, ForeignKey("autodiscovery_policies.id"), nullable=False, default=1)
    autodiscovery_policy = relationship('AutodiscoveryPolicy', backref='hosts')
    config_transfer_id = Column(Integer, ForeignKey('config_transfers.id'), nullable=False, default=1)
    config_transfer = relationship('ConfigTransfer')
    default_user_id = Column(Integer, ForeignKey('tg_user.user_id'))
    default_user = relationship('User')
    ifaces = relationship('Iface', backref='host', order_by='Iface.id')
    configs = relationship('HostConfig', backref='host', order_by='HostConfig.id', cascade='all, delete, delete-orphan')
    show_host = Column(Boolean, default=True)
    pollable = Column(Boolean, default=True)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.datetime.now)
    polled = Column(DateTime, nullable=False, default=datetime.datetime.now)
    sysobjid = Column(String(250))
    #}

    def __init__(self,mgmt_address=None,display_name=None):
        if mgmt_address is not None: self.mgmt_address = mgmt_address
        if display_name is not None: self.display_name = display_name
        #self.zone = zone.Zone.default()

    def __repr__(self):
        return '<Host: name=%s Address=%s>' % (self.display_name, self.mgmt_address)

    def __unicode__(self):
        return self.display_name

    @classmethod
    def by_address(cls, address):
        """ Return the host whose management addres is ``address''."""
        return DBSession.query(cls).filter(cls.mgmt_address==address).first()

    def snmp_scan_ifaces(self):
        for iface in self.ifaces:
            print(iface.ifindex)
        ifCount = snmp.get_int(self,(1,3,6,1,2,1,2,1,0),0)
        if ifCount == 0:
            return

        ifDescrs = snmp.walk(self,(1,3,6,1,2,1,2,2,1,2),rowCount=ifCount)
        if ifDescrs is None:
            return
        ifTypes = snmp.walk(self,(1,3,6,1,2,1,2,2,1,3),rowCount=ifCount)
        ifSpeeds = snmp.walk(self,(1,3,6,1,2,1,2,2,1,5),rowCount=ifCount)
        ifPhysAddrs = snmp.walk(self,(1,3,6,1,2,1,2,2,1,6),rowCount=ifCount)

        for ifIndex,ifDescr in ifDescrs.items():
            if any(iface.ifindex==ifIndex for iface in self.ifaces):
                continue 
            new_iface = Iface(ifindex=ifIndex,display_name=unicode(ifDescr))
            new_iface.iftype = int(ifTypes.get(ifIndex,1)) #1= type other
            new_iface.ifSpeed = int(ifSpeeds.get(ifIndex,0))
            new_iface.PhysAddr = str(ifPhysAddrs.get(ifIndex,''))
            self.ifaces.append(new_iface)

    def SnmpScan(self):
        updated = False
        if (self.community_ro is None or self.mgmt_address is None):
            return

        new_sysobjid = snmp.get(self, (1,3,6,1,2,1,1,2,0))
        if new_sysobjid:
            updated = True
            self.sysobjid = str(new_sysobjid)

        if not self.display_name or self.display_name == '':
            new_name = snmp.get(self, [1,3,6,1,2,1,1,5,0])
            if new_name:
                updated = True
                self.display_name = new_name

        self.snmp_scan_ifaces()


        # Update the updated column
        if updated:
            self.updated = datetime.datetime.now()

    def attrib_by_index(self, index):
        """ Return a host's attribute that has the given ''index''."""
        if self.attributes is None:
            return None
        str_index = str(index)
        for attrib in self.attributes:
            if attrib.index == str_index:
                return attrib
        return None

    def attribute_indexes(self, atype=None):
        """
        Return a list of attribute indexes for a given attribute type id
        if specified.
        """
        if self.attributes is not None:
            if atype == None:
                return [ attrib.index for attrib in self.attributes]
            else:
                return [ attrib.index for attrib in self.attributes if attrib.attribute_type_id == atype]
        return []

    

        

class Iface(DeclarativeBase):
    __tablename__ = 'interfaces'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=False)
    ifindex = Column(Integer, nullable=False) #ifIndex
    display_name = Column(Unicode(30)) #ifDescr or idXName
    iftype = Column(Integer, nullable=False,default=1) # other
    speed = Column(Integer)
    physaddr = Column(String(30)) #MAC address usually
    stacklower = Column(Integer, nullable=False,default=0) # ifStackLowerLayer
    ip4addr = Column(String(16))
    ip4bits = Column(SmallInteger)
    ip6addr = Column(String(40))
    ip6bits = Column(SmallInteger)
    #}

    def __init__(self, ifindex=None, display_name=None, iftype=None):
        self.host_id = 1
        self.ifindex = ifindex
        self.display_name = display_name
        self.iftype = iftype

class ConfigTransfer(DeclarativeBase):
    __tablename__ = 'config_transfers'
    
    def __init__(self, display_name=False, plugin_name=False):
        if display_name and plugin_name:
            self.display_name = display_name
            self.plugin_name = plugin_name
    #{ Columns
    id = Column(Integer, primary_key=True)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    plugin_name = Column(String(40), nullable=False, unique=True)
    #}

class HostConfig(DeclarativeBase):
    __tablename__ = 'host_configs'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    host_id = Column(Integer, ForeignKey('hosts.id'), nullable=False)
    config = Column(Text)

    def __init__(self,host=None, config=None):
        self.host = host
        self.config = config
