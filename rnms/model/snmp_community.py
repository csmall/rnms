# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
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
""" SNMP Community definition model """
from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode, String, SmallInteger

from pysnmp.proto import api
from pysnmp.entity.rfc3413.oneliner.auth import CommunityData, UsmUserData
from pysnmp.entity import config

from rnms.model import DeclarativeBase, DBSession

# Security Levels
AUTH_NONE = 0
AUTH_MD5 = 1
AUTH_SHA = 2
AUTH_MAX = AUTH_SHA

PRIV_NONE = 0
PRIV_DES = 1
PRIV_AES = 2
PRIV_MAX = PRIV_AES

AUTH_NAMES = {
    AUTH_NONE: u'None',
    AUTH_MD5:  u'MD5',
    AUTH_SHA:  u'SHA',
}

AUTH_PROTOCOLS = {
    AUTH_NONE: config.usmNoAuthProtocol,
    AUTH_MD5: config.usmHMACMD5AuthProtocol,
    AUTH_SHA: config.usmHMACSHAAuthProtocol,
}
PRIV_NAMES = {
    PRIV_NONE: u'None',
    PRIV_DES:  u'DES',
    PRIV_AES:  u'AES',
}

PRIV_PROTOCOLS = {
    PRIV_NONE: config.usmNoPrivProtocol,
    PRIV_DES: config.usmDESPrivProtocol,
    PRIV_AES: config.usmAesCfb128Protocol,
}


class SnmpCommunity(DeclarativeBase):
    __tablename__ = 'snmp_communities'
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    version = Column(SmallInteger, default=1)
    community = Column(String(40), nullable=False, default='')
    auth_type = Column(SmallInteger, default=AUTH_NONE)
    auth_passwd = Column(String(40))
    priv_type = Column(SmallInteger, default=PRIV_NONE)
    priv_passwd = Column(String(40))

    def __init__(self, display_name=None):
        self.display_name = display_name

    @classmethod
    def by_name(cls, name):
        """ Return community with given display_name """
        return DBSession.query(cls).filter(cls.display_name == name).first()

    @classmethod
    def by_id(cls, comm_id):
        """ Return community with given id """
        return DBSession.query(cls).filter(cls.id == comm_id).first()

    @property
    def security_name(self):
        """ security name is alias for community for v3 """
        return self.community

    @security_name.setter
    def security_name(self, value):
        self.community = value

    def is_empty(self):
        """ Returns True if this community is unset """
        return self.community == ''

    def is_snmpv1(self):
        """ Returns True if Community is SNMP v1 """
        return self.version == 1

    def is_snmpv2(self):
        """ Returns True if Community is SNMP v2 """
        return self.version == 2

    def proto_module(self):
        """ Return the protocol module for this SNMP version """
        if self.version == 1:
            return api.protoModules[api.protoVersion1]
        elif self.version in (2, 3):
            return api.protoModules[api.protoVersion2c]
        raise ValueError('Bad SNMP version {}'.format(self.version))

    def set_v1community(self, community):
        """ Make this a version 1 community """
        self.version = 1
        self.community = community
        self.auth_type = AUTH_NONE
        self.auth_passwd = None
        self.priv_type = AUTH_NONE
        self.priv_passwd = None

    def set_v2community(self, community):
        """ Make this a version 2c community """
        self.set_v1community(community)
        self.version = 2

    def set_v3auth_none(self):
        """ Make this a V3 community, with no authentication """
        self.version = 3
        self.community = None
        self.auth_type = AUTH_NONE
        self.auth_passwd = None

    def set_v3auth_md5(self, community, password):
        """ Set this to V3 community with MD5 password """
        self.version = 3
        self.community = community
        self.auth_type = AUTH_MD5
        self.auth_passwd = password

    def set_v3auth_sha(self, community, password):
        """ Set this to V3 community with SHA password """
        self.version = 3
        self.community = community
        self.auth_type = AUTH_SHA
        self.auth_passwd = password

    def set_v3privacy_none(self):
        """ Set version 3 privacy to none """
        self.priv_type = PRIV_NONE
        self.priv_passwd = None

    def set_v3privacy_des(self, password):
        """ Set version 3 privacy to DES with given password """
        self.priv_type = PRIV_DES
        self.priv_passwd = password

    def set_v3privacy_aes(self, password):
        """ Set version 3 privacy to AES with given password """
        self.priv_type = PRIV_AES
        self.priv_passwd = password

    def get_auth_data(self):
        """ Returns the authentication data that is used in the SNMP
        command generator """
        if self.version != 3:
            return CommunityData(self.community)
        return UsmUserData(self.community,
                           self.auth_passwd, self.priv_passwd,
                           AUTH_PROTOCOLS.get(self.auth_type,
                                              AUTH_PROTOCOLS[AUTH_NONE]),
                           PRIV_PROTOCOLS.get(self.priv_type,
                                              PRIV_PROTOCOLS[PRIV_NONE])
                           )
