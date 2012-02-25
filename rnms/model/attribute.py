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
"""Attributes for a host"""
import datetime
import logging

from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, metadata, DBSession

__all__ = ['Attribute', 'AttributeField', 'AttributeType', 'AttributeTypeField', 'AttributeTypeRRD', 'DiscoveredAttribute']

snmp_state_names = {1:'up', 2:'down', 3:'testing', 4:'unknown'}
class Attribute(DeclarativeBase):
    __tablename__ = 'attributes'
    
    #{ Columns
    id = Column(Integer, autoincrement=True,primary_key=True)
    display_name = Column(Unicode(40))
    oper_state = Column(SmallInteger, nullable=False) #IF-MIB
    admin_state = Column(SmallInteger, nullable=False) #IF-MIB
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    attribute_type=relationship('AttributeType',backref='attributes')
    host_id = Column(Integer, ForeignKey('hosts.id'))
    host = relationship('Host', backref='attributes')
    use_iface = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey('tg_user.user_id'),nullable=False)
    user = relationship('User', backref='attributes')
    sla_id = Column(Integer, ForeignKey('slas.id'),nullable=False)
    index = Column(String(40), nullable=False) # Unique for host
    make_sound = Column(Boolean,nullable=False)
    show_rootmap = Column(SmallInteger,nullable=False)
    poll_interval = Column(SmallInteger,nullable=False)
    check_status = Column(Boolean,nullable=False)
    poll_priority = Column(Boolean,nullable=False) #DMII
    poller_set_id = Column(Integer, ForeignKey('poller_sets.id'), nullable=False, default=1)
    poller_set = relationship('PollerSet')
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.datetime.now)
    polled = Column(DateTime, nullable=False, default=datetime.datetime.min)
    fields = relationship('AttributeField', backref='attribute', cascade='all, delete, delete-orphan')
    #}

    @classmethod
    def by_id(cls, attribute_id):
        """ Return the attribute with given id"""
        return DBSession.query(cls).filter(
                cls.id == attribute_id).first()

    @classmethod
    def by_display_name(cls, host, display_name):
        """" Return the attibute for a host matching display_name """
        if host is None or display_name is None:
            return None
        return DBSession.query(cls).filter(
                cls.host == host).filter(cls.display_name == display_name).first()

    @classmethod
    def from_discovered(cls, discovered_attribute):
        a = cls()
        a.host_id = discovered_attribute.host_id
        a.attribute_id = discovered_attribute.attribute_id
        a.display_name = discovered_attribute.display_name
        a.index = discovered_attribute.index
        a.use_iface = discovered_attribute.use_iface
        a.admin_state = discovered_attribute.admin_state
        a.oper_state = discovered_attribute.oper_state
        for field in discovered_attribute.fields:
            print "Field is %s" % field
        return a

    def __init__(self, host=None, attribute_type=None, display_name=None, index=''):
        self.host=host
        self.attribute_type=attribute_type
        self.display_name=display_name
        self.index = index
        self.oper_state=2
        self.admin_state=2
        self.use_iface = False
        self.user_id = 1
        self.sla_id = 1
        self.make_sound = True
        self.show_rootmap = 0
        self.poll_interval = 0
        self.check_status = True
        self.poll_priority = False
        self.poller_set_id = 1

    def __repr__(self):
        return '<Attribute name=%s>' % self.display_name

    def add_field(self, tag, value):
        """ Add a new field that has ''tag'' with the value ''value''"""
        type_field = AttributeTypeField.by_tag(self.attribute_type, tag)
        if type_field is None:
            logging.warning("Cannot find field '%s' for attribute type.", tag)
            return
        new_field = AttributeField(self,type_field)
        new_field.value = value

    def get_field(self, tag, default=None):
        """ Get value of field for this attribute with tag='tag'. """
        type_field = AttributeTypeField.by_tag(self.attribute_type, tag)
        if type_field is None:
            return default
        for field in self.fields:
            if field.attribute_type_field_id == type_field.id:
                return field.value
        return default

    def query(self):
        return DBSession
        
    def oper_state_name(self):
        """ Return string representation of operational state"""
        if self.oper_state in snmp_state_names:
            return snmp_state_names[self.oper_state]
        return u"Unknown {0}".format(self.oper_state)

    def admin_state_name(self):
        """ Return string representation of admin state"""
        if self.admin_state in snmp_state_names:
            return snmp_state_names[self.admin_state]
        return u"Unknown {0}".format(self.admin_state)


class AttributeField(DeclarativeBase):
    __tablename__ = 'attribute_fields'
    
    #{ Columns
    id = Column(Integer, autoincrement=True,primary_key=True)
    attribute_id = Column(Integer, ForeignKey('attributes.id'),nullable=False)
    attribute_type_field_id = Column(Integer, ForeignKey('attribute_type_fields.id'),nullable=False)
    attribute_type_field = relationship('AttributeTypeField')
    value = Column(String(250))

    def __init__(self, attribute=None, attribute_type_field=None):
        self.attribute = attribute
        self.attribute_type_field = attribute_type_field
        self.value=''

    def overwritable(self):
        if self.attribute_type_field is None:
            return False
        return self.attribute_type_field.overwritable

    def tag(self):
        if self.attribute_type_field is None:
            return None
        return self.attribute_type_field.tag

class AttributeType(DeclarativeBase):
    __tablename__ = 'attribute_types'
    
    #{ Columns
    id = Column(Integer, autoincrement=True,primary_key=True)
    display_name = Column(Unicode(50),unique=True,nullable=False)
    ad_validate = Column(Boolean, nullable=False)
    ad_enabled = Column(Boolean, nullable=False)
    ad_function = Column(String(50),nullable=False)
    ad_parameters = Column(String(200))
    #default_poller_id = Column(Integer, ForeignKey('poller_sets.id'))
    #FIXME circular default_poller = relationship('PollerSet')
    rra_cf = Column(String(10), nullable=False, default='AVERAGE')
    rra_rows = Column(Integer, nullable=False, default=103680)
    #default_graph_id = Column(Integer, ForeignKey('graph_type_graphs.id'))
    #FIXME circular default_graph = relationship('GraphTypeGraph')
    break_by_card = Column(Boolean, nullable=False, default=False)
    permit_manual_add = Column(Boolean, nullable=False, default=False)
    #default_sla_id = Column(Integer, ForeignKey('slas.id'))
    required_sysobjid = Column(String(250), nullable=False)
    slas = relationship('Sla', order_by='Sla.id', backref='attribute_type')
    fields = relationship('AttributeTypeField', order_by='AttributeTypeField.position', backref='attribute_type', cascade='all, delete, delete-orphan')
    rrds = relationship('AttributeTypeRRD', order_by='AttributeTypeRRD.position', backref='attribute_type', cascade='all, delete, delete-orphan')
    #}
    def __init__(self, display_name=None, ad_function='none', ad_parameters=''):
        self.display_name=display_name
        self.ad_enabled=False
        self.ad_validate = False
        self.ad_function = ad_function
        self.ad_parameters= ad_parameters
        self.required_sysobjid=''

class AttributeTypeField(DeclarativeBase):
    __tablename__ = 'attribute_type_fields'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    attribute_type_id = Column(Integer, ForeignKey("attribute_types.id"),nullable=False)
    display_name = Column(Unicode(40),nullable=False)
    tag = Column(String(40))
    position = Column(SmallInteger,nullable=False,default=10)
    description = Column(Boolean,nullable=False,default=False)
    showable_edit = Column(Boolean,nullable=False,default=True)
    showable_discovery = Column(Boolean,nullable=False,default=True)
    overwritable = Column(Boolean,nullable=False,default=True)
    tracked = Column(Boolean,nullable=False,default=False)
    default_value = Column(String(250))
    parameters = Column(String(250))
    backend = Column(String(40))
    #}
    
    @classmethod
    def by_tag(cls, attribute_type, tag):
        """ Return the field for attribute type with id that has tag ''tag''."""
        return DBSession.query(cls).filter(and_(
                cls.attribute_type_id == attribute_type,
                cls.tag==tag)).first()

        

class AttributeTypeRRD(DeclarativeBase):
    __tablename__ = 'attribute_type_rrds'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    attribute_type_id = Column(Integer, ForeignKey("attribute_types.id"),nullable=False)
    display_name = Column(Unicode(40), nullable=False)
    name = Column(String(40))
    position = Column(SmallInteger,nullable=False,default=10)
    data_source_type = Column(SmallInteger) # gauge,counter,absolute
    range_min = Column(Integer)
    range_max = Column(Integer)
    range_max_field = Column(Integer,ForeignKey('attribute_type_fields.id')) # foreign key to attribute_type_value
    #}

# Discovered Attributes do not have and database backend
class DiscoveredAttribute():
    """
    Attributes that are disocvered through the autodisovery process
    do not have any database backend but just lists
    """

    def __init__(self, host_id=1, attribute_type_id=1):
        self.host_id=host_id
        self.display_name = ''
        self.oper_state = 2
        self.admin_state = 2
        self.attribute_type_id=attribute_type_id
        self.index = ''
        fields = {}

    def add_field(self, key, value):
        self.fields[key] = value

