# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011,2012 Craig Small <csmall@enc.com.au>
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
from sqlalchemy.orm import mapper, relationship, subqueryload
from sqlalchemy import Table, ForeignKey, Column, and_
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, metadata, DBSession
from rnms.model.host import Host

__all__ = ['Attribute', 'AttributeField', 'AttributeType', 'AttributeTypeField', 'AttributeTypeRRD', 'DiscoveredAttribute']

snmp_state_names = {1:'up', 2:'down', 3:'testing', 4:'unknown'}
class Attribute(DeclarativeBase):
    __tablename__ = 'attributes'
    
    #{ Columns
    id = Column(Integer, autoincrement=True,primary_key=True)
    display_name = Column(Unicode(40))
    description = Column(Unicode(200))
    oper_state = Column(SmallInteger, nullable=False) #IF-MIB
    admin_state = Column(SmallInteger, nullable=False) #IF-MIB
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    attribute_type=relationship('AttributeType',backref='attributes')
    host_id = Column(Integer, ForeignKey('hosts.id'))
    host = relationship('Host', backref='attributes')
    use_iface = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey('tg_user.user_id'),nullable=False)
    user = relationship('User', backref='attributes')
    sla_id = Column(Integer, ForeignKey('slas.id', use_alter=True, name='fk_sla'),nullable=False)
    sla = relationship('Sla', primaryjoin='Attribute.sla_id==Sla.id', post_update=True)
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
    next_poll = Column(DateTime, nullable=False, default=datetime.datetime.min)
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

    @classmethod
    def have_sla(cls, attribute_id=None):
        """ Return attributes have have a SLA set plus polling """
        return DBSession.query(cls).options(subqueryload('sla')).filter(cls.sla_id > 1)
        if attribute_id is None:
            return DBSession.query(cls).join(Host).filter(and_( (cls.poller_set_id > 1),(Host.pollable==True)))
        else:
            return DBSession.query(cls).join(Host).filter(and_( (cls.poller_set_id > 1),(Host.pollable==True), (cls.id == attribute_id)))

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

    def get_fields(self):
        """ Return a dictionary of all fields for this attribute"""
        fields={}
        for at_field in self.attribute_type.fields:
            fields[at_field.tag]=self.field(id=at_field.id)
        return fields

    def field(self, tag=None, id=None):
        """ Get value of field for this attribute with tag='tag'. """
        at_field = None
        if tag is not None:
            at_field = AttributeTypeField.by_tag(self.attribute_type, tag)
        elif id is not None:
            at_field = AttributeTypeField.by_id(id)
        if at_field is None:
            return None
        for field in self.fields:
            if field.attribute_type_field_id == at_field.id:
                return field.value
        return at_field.default_value

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

    def is_down(self):
        """
        Return true if this attribute is down. A down interface is one that
        has current down alarms"""
        for alarm in self.alarms:
            if alarm.is_down():
                return True
        return False

    def fetch_rrd_value(self, start_time, end_time, rrd_name):
        """
        Return rrd value for the given time
        """
        # FIXME
        at_rrd = AttributeTypeRRD.by_name(self.attribute_type,rrd_name)
        if at_rrd is None:
            return None
        print "interface-{0}-{1}\n".format(self.id,at_rrd.position)
        print "fetch rrd name {0}\n".format(rrd_name)
        return 42

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
    #default_graph_id = Column(Integer, ForeignKey('graph_type_graphs.id', use_alter=True, name='fk_default_graph'))
    #default_graph = relationship('GraphTypeGraph', primaryjoin='AttributeType.id==Graph.attribute_type_id', post_update=True)
    break_by_card = Column(Boolean, nullable=False, default=False)
    permit_manual_add = Column(Boolean, nullable=False, default=False)
    required_sysobjid = Column(String(250), nullable=False)
    default_sla_id = Column(Integer, ForeignKey('slas.id', use_alter=True, name='fk_default_sla'))
    default_sla = relationship('Sla', primaryjoin='AttributeType.default_sla_id==Sla.id', post_update=True)
    slas = relationship('Sla', order_by='Sla.id', backref='attribute_type',
            primaryjoin='AttributeType.id==Sla.attribute_type_id')
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

    @classmethod
    def by_id(cls, id):
        """ Return the field with given id"""
        return DBSession.query(cls).filter(cls.id==id).first()

class AttributeTypeRRD(DeclarativeBase):
    """
    AttributeTypes may have RRD fields attached to their definition
    """
    __tablename__ = 'attribute_type_rrds'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    attribute_type_id = Column(Integer, ForeignKey("attribute_types.id"),nullable=False)
    display_name = Column(Unicode(40), nullable=False)
    name = Column(String(40))
    position = Column(SmallInteger,nullable=False,default=1)
    data_source_type = Column(SmallInteger) # gauge,counter,absolute
    range_min = Column(Integer)
    range_max = Column(Integer)
    range_max_field = Column(String(40)) # matches tag in fields
    #}

    @classmethod
    def by_name(cls, attribute_type, name):
        """ Return the RRD for this attribute_type with the given name """
        print "by name {0} and name {1}".format(attribute_type.id, name)
        return DBSession.query(cls).filter(and_(
                cls.attribute_type_id == attribute_type.id,
                cls.name==name)).first()



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

