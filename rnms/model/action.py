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

""" Action template """
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, metadata, DBSession


class Action(DeclarativeBase):
    __tablename__ = 'actions'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40))
    tag = Column(String(40),nullable=False)
    fields = relationship('ActionField')
    internal_fields = Column(String(120))
    #}
    defined_actions = ('email', 'smsclient')

    def get_trigger_fields(self, trigger):
        """
        Return a dictionary of the action fields based upon internal_fields
        of this model and the action fields of the trigger.
        These will still be the templates, the values from event/alarm
        will be filled in later.
        """
        fields = {}
        for pairs in self.internal_fields.split(','):
            pair = pairs.split(':')
            if len(pair) != 2:
                continue
            fields[pair[0]]=pair[1]
        for trigger_field in trigger.action_fields:
            fields[trigger_field.action_field.tag] = trigger_field.value
        return fields

    def run_alarm(self, trigger, alarm):
        """
        Run this action for an alarm trigger
        """
        raw_fields = self.get_trigger_fields(trigger)
        subs = alarm.substitutes()

        self.email(raw_fields)
            

        

    def email(self, fields):
        """
        The email action. Sends an email to the specified user.
        """
        to_address = fields['to']
        from_address = fields['from']
        subject = fields['subject']
        body=[]

        if 'short' in fields and fields['short']==1:
            short_email = True
            body_delimiter=' '
        else:
            short_email = False
            body.append('Hello {0}'.format(fields['']))
            body_delimiter='\n'

        if 'alarm' in fields:
            alarm=fields['alarm']
            alarm_text='Alarm Time:\t{0}'.format(alarm.start_time)
            if alarm.is_up():
                alarm_text +=' To {0}'.format(alarm.stop_time)
            body.append(alarm_text)
            body.append('Alarm Type: {0} {1}'.format(
                alarm.event_type.display_name,
                alarm.alarm_state.display_name))

        if 'attribute' in fields:
            att=fields['attribute']
            body.append('Attribute:\t {0} {1} {2} {3} {4} {5}'.format(
                att.attribute_type.display_name,
                att.host.display_name,
                att.zone.display_name,
                att.user.display_name,
                'FIXME'))
        if 'events' in fields:
            for event in events:
                body.append('Event:\t {0} {1}'.format(
                    event.created, event.event_type.display_name))

        body_text = body_delimiter.join(body)
            








class ActionField(DeclarativeBase):
    """
    Fields that are used in actions but are presented in the trigger.
    """
    __tablename__ = 'action_fields'
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    action_id = Column(Integer, ForeignKey('actions.id'), nullable=False)
    tag = Column(Unicode(40), nullable=False, default=u'')
    display_name = Column(Unicode(40), nullable=False, default=u'')

