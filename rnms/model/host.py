# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011,2013 Craig Small <csmall@enc.com.au>
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
import transaction
import random

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, Boolean, PickleType, String, DateTime, Text, SmallInteger, BigInteger

from rnms.model import DeclarativeBase, DBSession

__all__ = ['Host', 'Iface', 'ConfigTransfer', 'HostConfig', 'SnmpCommunity']

MINDATE=datetime.date(1900,1,1)
discover_interval = 30.0 # 30 min
discover_variance = 10.0 # +- 5 minutes next discovery

class Host(DeclarativeBase):
    __tablename__ = 'hosts'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    mgmt_address = Column(String(40))
    display_name = Column(String(255), nullable=False)
    zone_id = Column(Integer, ForeignKey('zones.id'))
    tftp_server = Column(String(40))
    snmp_community_id = Column(Integer, ForeignKey("snmp_communities.id"))
    snmp_community = relationship('SnmpCommunity')
    autodiscovery_policy_id = Column(Integer, ForeignKey("autodiscovery_policies.id") )
    autodiscovery_policy = relationship('AutodiscoveryPolicy', backref='hosts')
    config_transfer_id = Column(Integer, ForeignKey('config_transfers.id'))
    config_transfer = relationship('ConfigTransfer')
    default_user_id = Column(Integer, ForeignKey('tg_user.user_id'))
    default_user = relationship('User')
    attributes = relationship('Attribute', backref='host', cascade='all,delete,delete-orphan')
    ifaces = relationship('Iface', backref='host', order_by='Iface.id')
    configs = relationship('HostConfig', backref='host', order_by='HostConfig.id', cascade='all, delete, delete-orphan')
    traps = relationship('SnmpTrap', backref='host')
    show_host = Column(Boolean, default=True)
    pollable = Column(Boolean, default=True)
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.datetime.now)
    next_discover = Column(DateTime, nullable=False, default=datetime.datetime.now)
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
    def by_id(cls, hostid):
        """ Return the host whose id is hostid """
        return DBSession.query(cls).filter(cls.id==hostid).first()

    @classmethod
    def by_address(cls, address):
        """ Return the host whose management addres is ``address''."""
        if address[:7] == '::ffff:':
            return DBSession.query(cls).filter(cls.mgmt_address==address[7:]).first()
        return DBSession.query(cls).filter(cls.mgmt_address==address).first()

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

    def main_attributes_down(self):
        """
        Return true if the attributes for the host that have poll_priority
        set are considered down
        """
        for attribute in self.attributes:
            if attribute.poll_priority and attribute.is_down():
                return True
        return False

    def ro_is_snmpv1(self):
        """ Returns True if Read Only Community is SNMP v1 """
        return self.snmp_community.ro_is_snmpv1()

    def update_discover_time(self):
        """
        Update the next discover date to the next time we auto-discover
        on this host.
        """
        self.next_discover = datetime.datetime.now() + datetime.timedelta(
                seconds = (discover_interval + (random.random() - 0.5) * discover_variance) * 60.0)
        transaction.commit()

class Iface(DeclarativeBase):
    __tablename__ = 'interfaces'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    host_id = Column(Integer, ForeignKey("hosts.id"), nullable=False)
    ifindex = Column(Integer, nullable=False) #ifIndex
    display_name = Column(Unicode(30)) #ifDescr or idXName
    iftype = Column(Integer, nullable=False,default=1) # other
    speed = Column(BigInteger)
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

class SnmpCommunity(DeclarativeBase):
    __tablename__ = 'snmp_communities'
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    readonly = Column(PickleType, default='')
    readwrite = Column(PickleType, default='')
    trap = Column(PickleType, default='')

    @classmethod
    def by_name(cls, name):
        """ Return community with given display_name """
        return DBSession.query(cls).filter(cls.display_name == name).first()

    def ro_is_snmpv1(self):
        """ Returns True if Read Only Community is SNMP v1 """
        return self.readonly != '' and self.readonly[0] == '1'

    def ro_is_snmpv2(self):
        """ Returns True if Read Only Community is SNMP v2 """
        return self.readonly != '' and self.readonly[0] == '2'
