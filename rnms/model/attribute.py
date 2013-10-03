# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011,2012,2013 Craig Small <csmall@enc.com.au>
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
import random

from sqlalchemy.orm import relationship, subqueryload
from sqlalchemy import ForeignKey, Column, and_, asc
from sqlalchemy.types import Integer, Unicode, String, Boolean, SmallInteger, DateTime
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, DBSession
from rnms.lib import states
from rnms.lib.parsers import fill_fields

__all__ = ['Attribute', 'AttributeField', 'AttributeType', 'AttributeTypeField', 'DiscoveredAttribute']
logger = logging.getLogger('rnms')

MINDATE=datetime.date(1900,1,1)
POLL_VARIANCE_MINUTES = 1 # +- 30 seconds for next poll

# Check the SLAs every 30 minuts += 2 minutes
SLA_INTERVAL_MINUTES = 30
SLA_VARIANCE_MINUTES = 2

class Attribute(DeclarativeBase):
    __tablename__ = 'attributes'
    default_poll_interval = 5
    display_name_len = 40

    #{ Columns
    id = Column(Integer, autoincrement=True,primary_key=True)
    display_name = Column(Unicode(display_name_len))
    admin_state = Column(SmallInteger, nullable=False) #IF-MIB
    state_id = Column(Integer, ForeignKey('event_states.id'))
    state = relationship('EventState')
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    attribute_type=relationship('AttributeType',backref='attributes')
    host_id = Column(Integer, ForeignKey('hosts.id', ondelete="CASCADE", onupdate="CASCADE"))
    use_iface = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey('tg_user.user_id'),nullable=False)
    user = relationship('User', backref='attributes')
    sla_id = Column(Integer, ForeignKey('slas.id', use_alter=True, name='fk_sla'),nullable=False, default=1)
    sla = relationship('Sla', primaryjoin='Attribute.sla_id==Sla.id', post_update=True)
    index = Column(String(40), nullable=False) # Unique for host
    make_sound = Column(Boolean,nullable=False)
    poll_interval = Column(SmallInteger,nullable=False, default=0)
    poll_enabled = Column(Boolean, nullable=False, default=True)
    check_status = Column(Boolean,nullable=False)
    poll_priority = Column(Boolean,nullable=False) #DMII
    poller_set_id = Column(Integer, ForeignKey('poller_sets.id'))
    poller_set = relationship('PollerSet')
    created = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updated = Column(DateTime, nullable=False, default=datetime.datetime.now)
    next_poll = Column(DateTime, nullable=False, default=datetime.datetime.now)
    next_sla = Column(DateTime, nullable=False, default=datetime.datetime.now)
    fields = relationship('AttributeField', backref='attribute', cascade='all, delete, delete-orphan')
    #}

    def __init__(self, host=None, attribute_type=None, display_name=None, index=''):
        self.host=host
        self.attribute_type=attribute_type
        self.display_name=display_name
        self.index = index
        self.admin_state = states.STATE_UNKNOWN
        self.use_iface = False
        self.user_id = 1
        self.sla_id = 1
        self.make_sound = True
        self.poll_interval = 0
        self.check_status = True
        self.poll_priority = False
        self.poller_set_id = 1

    def __repr__(self):
        return '<Attribute name=%s>' % self.display_name

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
    def next_polled(cls):
        """
        Return the attribute that would be the next polled one
        Used for finding how long before we need to rescan again
        """
        down_host_ids = []
        attributes = DBSession.query(cls).order_by(asc(cls.next_poll))
        for attribute in attributes:
            if attribute.poll_priority:
                return attribute # priority attributes always are used
            if attribute.host_id in down_host_ids:
                continue
            if attribute.host.main_attributes_down():
                down_host_ids.append(attribute.host_id)
                continue
            return attribute
        return None


    
    @classmethod
    def next_sla_analysis(cls):
        """
        Return the attribute that would be the next one for SLA
        Used for finding how long before we need to rescan again
        """
        return DBSession.query(cls).filter(and_(cls.sla_id > 1, cls.poller_set_id > 1)).order_by(asc(cls.next_sla)).first()

    @classmethod
    def from_discovered(cls, host, discovered_attribute):
        """
        Create a real Attribute object based upon data that is found in the
        fake DiscoveredAttribute object
        """
        from rnms.model import EventState
        a = cls()
        a.host_id = discovered_attribute.host_id
        a.attribute_type = discovered_attribute.attribute_type
        a.display_name = discovered_attribute.display_name
        a.index = discovered_attribute.index
        #a.use_iface = discovered_attribute.use_iface
        a.admin_state = discovered_attribute.admin_state
        a.user_id = host.default_user_id
        # SLA default needed
        a.state = EventState.get_up()

        for tag,value in discovered_attribute.fields.items():
            a.set_field(tag,value)

        if host.autodiscovery_policy.set_poller and a.attribute_type.default_poller_set_id is not None:
            a.poller_set_id = a.attribute_type.default_poller_set_id
        return a

    @classmethod
    def have_sla(cls, next_sla_time=None, attribute_ids=None, host_ids=None):
        """ Return attributes have have a SLA set plus polling """
        conditions = [cls.sla_id > 1, cls.poller_set_id > 1]
        if next_sla_time is not None:
            conditions.append(cls.next_sla < next_sla_time)
        if attribute_ids is not None:
            conditions.append(cls.id.in_(attribute_ids))
        if host_ids is not None:
            conditions.append(cls.host_id.in_(host_ids))
        return DBSession.query(cls).options(subqueryload('sla')).filter(and_(*conditions))

    def set_field(self, tag, value):
        """ Add a new field that has ''tag'' with the value ''value''"""
        type_field = AttributeTypeField.by_tag(self.attribute_type, tag)
        if type_field is None:
            logger.warning("Cannot find field '%s' for attribute type.", tag)
            return
        for field in self.fields:
            if field.attribute_type_field_id == type_field.id:
                if field.value != value:
                    field.value = value
        else:
            new_field = AttributeField(self,type_field)
            new_field.value = value

    def get_fields(self):
        """ Return a dictionary of all fields for this attribute"""
        fields={}
        for at_field in self.attribute_type.fields:
            fields[at_field.tag]=self.get_field(id=at_field.id)
        return fields

    def get_field(self, tag=None, id=None):
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

    def get_rrd_value(self, rrd_name, start_time, end_time):
        """
        Return the value for the RRD with start and stop time
        Raises KeyError if rrd_name not found
        """
        for at_rrd in self.attribute_type.rrds:
            if at_rrd.name == rrd_name:
                return at_rrd.get_average_value(self.id, start_time, end_time)
        raise KeyError('Attribute has no RRD {}'.format(rrd_name))

    def description_dict(self):
        """
        Return a dictionary of the Attributes description fields
        """
        if self.attribute_type is None:
            return {}
        return { at_field.display_name: self.get_field(id=at_field.id) for at_field in self.attribute_type.fields if at_field.description}

    def description(self):
        """ Returns a string of all joined description fields """
        if self.attribute_type is None:
            return ''
        descriptions = [ self.get_field(id=at_field.id) for at_field in self.attribute_type.fields if at_field.description]
        return " ".join(descriptions)

    def oper_state_name(self):
        """ Return string representation of operational state"""
        if self.state is None:
            return 'Unknown'
        else:
            return self.state.display_name

    def admin_state_name(self):
        """ Return string representation of admin state"""
        try:
            return states.STATE_NAMES[self.admin_state]
        except KeyError:
            return u"Unknown {0}".format(self.admin_state)

    def set_admin_state(self, state_name):
        """ Set the admin_state based upon a state_name """
        for state,name in states.STATE_NAMES.items():
            if state_name == name:
                self.admin_state = state
                return True
        return False

    def is_down(self):
        """ Return true if this attribute is down. """
        return self.state is None or self.state.internal_state == states.STATE_DOWN

    def update_poll_time(self):
        """
        Update the next poll time 
        """
        now = datetime.datetime.now()
        next_poll_variance = datetime.timedelta(minutes=(random.random() - 0.5) * POLL_VARIANCE_MINUTES * 2)
        if self.poll_interval < 1:
            self.next_poll = now + datetime.timedelta(minutes=self.default_poll_interval) + next_poll_variance
        else:
            self.next_poll = now + datetime.timedelta(minutes=self.poll_interval) + next_poll_variance
    
    def update_sla_time(self):
        """
        Update the next time we run the SLA analysis for this attribute
        """
        self.next_sla = datetime.datetime.now() + datetime.timedelta(minutes=(
            SLA_INTERVAL_MINUTES + (random.random()-0.5) * SLA_VARIANCE_MINUTES * 2))

    def set_disabled(self):
        """
        Set this Attribute to disabled. This means that there will be no
        ongoing polling for this Attibute and it's admin status is
        down
        """
        self.poll_enabled = False
        self.admin_status = states.STATE_DOWN

    def parse_string(self, raw_string):
        """
        Parse a string by replacing all the <key> with values from this
        attribute
        """
        return fill_fields(raw_string, attribute=self)

    def calculate_oper(self):
        """
        Work out what the current Oper state is for this attribute by
        looking at all the current events for this Attribute
        The calculated result is placed into the oper field
        """
        from rnms.model.event import EventState, Event
        att_event = Event.attribute_alarm(self.id)
        if att_event is None:
            self.state = EventState.by_name(u'up')
        else:
            self.state = att_event.event_state


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

    @classmethod
    def field_value(cls, attribute_id, field_tag):
        """ Return the value of the field for the given attribute that
        matches the tag
        """
        ftag = DBSession.query(AttributeTypeField).\
                join(AttributeType,Attribute).filter(
            Attribute.id == attribute_id,
            AttributeTypeField.tag == field_tag).first()
        if ftag is None:
            return None
        fval = DBSession.query(cls.value).filter(
            cls.attribute_id == attribute_id,
            cls.attribute_type_field_id == ftag.id).first()
        if fval is not None:
            return fval
        return ftag.default_value

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
    ad_command = Column(String(50),nullable=False)
    ad_parameters = Column(String(200))
    default_poller_set_id = Column(Integer, ForeignKey('poller_sets.id', use_alter=True, name='fk_atype_pollerset'))
    default_poller_set = relationship('PollerSet', primaryjoin='PollerSet.id == AttributeType.default_poller_set_id')
    ds_heartbeat = Column(Integer, nullable=False, default=600)
    rra_cf = Column(String(10), nullable=False, default='AVERAGE')
    rra_rows = Column(Integer, nullable=False, default=103680)
    default_graph_id = Column(Integer, ForeignKey('graph_types.id', use_alter=True, name='fk_atype_graph'))
    default_graph = relationship('GraphType', primaryjoin='GraphType.id== AttributeType.default_graph_id')
    graph_types = relationship('GraphType', primaryjoin='AttributeType.id == GraphType.attribute_type_id', backref='attribute_type')
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
    def __init__(self, display_name=None, ad_command='none', ad_parameters=''):
        self.display_name=display_name
        self.ad_enabled=False
        self.ad_validate = False
        self.ad_command = ad_command
        self.ad_parameters= ad_parameters
        self.required_sysobjid=''

    @classmethod
    def by_display_name(cls, display_name):
        """" Return the AttributeType matching display_name """
        if display_name is None:
            return None
        return DBSession.query(cls).filter(cls.display_name == display_name).first()

    @classmethod
    def name_by_id(cls, atype_id):
        """ Return AttributeType name for given ID """
        return DBSession.query(cls.display_name).select_from(cls).\
                filter(cls.id == atype_id).scalar()

    def autodiscover(self, dobj, host, force):
        """
        Attempt to autodiscover attributes of this object's type on the
        given host.
        Parameters:
          host: The host to query
        Returns:
          True/False - if it was enabled
          Will run a callback when the data is collected
        """
        if self.ad_command is None or self.ad_command == 'none':
            return False
        
        dobj.logger.debug('H:%d AT:%d Autodiscovering %s', host.id, self.id, self.display_name)
        if force == False and self.ad_enabled == False:
            return False
        if self._match_sysobjid(host) == False:
            return False

        from rnms.lib import att_discovers
        try:
            real_discover = getattr(att_discovers, 'discover_'+self.ad_command)
        except AttributeError:
            dobj.logger.error('H:%d AT:%d Attribute Discovery function "discover_%s" does not exist.', host.id, self.id, self.ad_command)
            return False
        return real_discover(dobj, self, host)
        return True

    def _match_sysobjid(self, host):
        """
        Check that the sysObjectId of the host matches or is a subset
        of the required systemobject id
        AttributeTypes may use ent. instead of 1.3.6.1.4.1.
        Returns true/false
        """
        if self.required_sysobjid == '':
            return True
        if host.sysobjid is None or host.sysobjid == '':
            logger.debug('H:%d AT:%d Skipping due to missing sysObjectId', host.id, self.id)
            return False
        if self.required_sysobjid == '.' and host.sysobjid != '':
            return True
        if host.sysobjid[len(self.required_sysobjid):] == self.required_sysobjid:
            return True
        sysid = self.required_sysobjid.replace('1.3.6.1.4.1.','ent.', 1)
        if host.sysobjid[:len(sysid)] == sysid:
            return True
        logger.debug('H:%d AT:%d Skipping due to sysObjectId (%s != %s)', host.id, self.id, host.sysobjid[:len(sysid)], sysid)
        return False

    def field_by_tag(self, tag):
        """
        Return the AttributeType field that matches the tag or None
        """
        for f in self.fields:
            if f.tag == tag:
                return f
        return None

    def get_graph_type(self):
        """ Return the default, or just one GraphType """
        try:
            return self.graph_types[0]
        except IndexError:
            return None


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
                cls.attribute_type == attribute_type,
                cls.tag==tag)).first()

    @classmethod
    def by_id(cls, id):
        """ Return the field with given id"""
        return DBSession.query(cls).filter(cls.id==id).first()

# Discovered Attributes do not have and database backend
class DiscoveredAttribute(object):
    """
    Attributes that are disocvered through the autodisovery process
    do not have any database backend but just lists.
    state is just used as a indicator on the GUI, its not
    transferred to the real Attribute.
    """

    def __init__(self, host_id=1, attribute_type=None):
        self.host_id=host_id
        self.display_name = ''
        self.admin_state = 'up'
        self.oper_state = 'up'
        self.attribute_type=attribute_type
        self.index = ''
        self.fields = {}

    def set_field(self, key, value):
        self.fields[key] = value

    def get_field(self, key):
        try:
            return self.fields[key]
        except KeyError:
            return None

    def oper_down(self):
        self.oper_state = 'down'

    def oper_unknown(self):
        self.oper_state = 'unknown'

    def admin_down(self):
        self.admin_state = 'down'

    def admin_unknown(self):
        self.admin_state = 'unknown'
