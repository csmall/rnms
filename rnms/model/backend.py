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
"""
Model for Backend processes

"""
import datetime

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, metadata, DBSession, EventType, AlarmState, Event, Alarm


class Backend(DeclarativeBase):
    """
    Poller and SNMP trap backends
    The backend is used for pollers and for trap receivers and generally
    is used to raise alarms/events or to set something in the database.

    All backends have the same set of arguments:
        attribute     - Attribute that was polled
        poller_result - Output from the poller. Can be string or
          dictionary but its the same for same backend type.
    Backends should return a string that describes the status. This
    string appears in the logs.
    """
    __tablename__ = 'backends'
    available_backends = [ 'event', 'event_always', 'admin_status', 'oper_status', 'verify_index']
    
    #{ Columns
    id = Column(Integer, primary_key=True, nullable=False)
    display_name = Column(Unicode(40), nullable=False, unique=True)
    command = Column(String(20))
    parameters = Column(String(250))

    def __init__(self,display_name=None, command='', parameters=''):
        self.display_name = display_name
        self.command = command
        self.parameters = parameters

    def __repr__(self):
        return '<Backend name=%s command=%s>' % (self.display_name, self.command)
    def __unicode__(self):
        return self.display_name

    @classmethod
    def by_display_name(cls, display_name):
        """ Return Backend with given class name"""
        return DBSession.query(cls).filter(cls.display_name == display_name).first()
    @classmethod
    def default(cls):
        """ Return Bakend that does nothing, the default """
        return DBSession.query(cls).filter(cls.id == 1).first()

    def run(self, poller_row, attribute, poller_result):
        """
        Run the real backend method "_run_BLAH" based upon the command 
        used
        """
        if self.command is None or self.command=='none' or self.command=='':
            return ''
        if self.command not in self.available_backends:
            return 'invalid backend {0}'.format(self.command)

        try:
            real_backend = getattr(self, "_run_"+self.command)
        except AttributeError:
            logging.error("Backend {0} does not exist.".format(self.command))
            return None
        else:
            return real_backend(poller_row, attribute, poller_result)

    def _run_event(self, poller_row, attribute, poller_result, always=False):
        """
        Backend: event
        Raises an event if required.
        poller parameters: <event_type_id>,[<default>],[<damp_time>]
        event_type_id: ID for the event to raise
        default:       if poller_result is nothing use this string
        damp_time:     time to wait before raising event
        poller_result: dictionary
           state - optional display_name to match AlarmState model
           other items are copied into event fields
        """

        params = self.parameters.split(',')
        try:
            event_type_id = int(params[0])
        except ValueError:
            return "EventType ID \"{0}\" is not an integer.".format(params[0])
        event_type = EventType.by_id(event_type_id)
        if event_type is None:
            return "ID \"{0}\" is not found in EventType table.".format(even_type_id)
        try:
            default_input = params[1]
        except IndexError:
            default_input = ''

        try:
            damp_time = int(params[2])
        except IndexError, ValueError:
            damp_time = 1

        event_fields={}
        if type(poller_result) is not dict:
            alarm_description = unicode(poller_result)
        else:
            try:
                alarm_description = poller_result['state']
                event_fields = {k:v for k,v in poller_result.items() if k!='state'}
            except KeyError:
                if default_input == '':
                    alarm_description='down'
                elif default_input != 'nothing':
                    alarm_description = default_input

        alarm_state = AlarmState.by_name(alarm_description)
        if alarm_state is None:
            return "Description \"{0}\" is not found in AlarmState table.".format(alarm_description)

        if always==True or self._backend_raise_event(attribute, event_type, alarm_state, damp_time):
            new_event = Event(event_type=event_type, 
                    attribute=attribute, alarm_state=alarm_state,
                    field_list=event_fields)
            DBSession.add(new_event)
            new_event.process()
            return "Event added: {0}".format(new_event.id)
        else:
            return "Nothing was done"

    def _run_event_always(self, poller_row, attribute, poller_result):
        """
        Backend: event_always
        Unconditionally raise an event
        poller parameters: <event_type_id>
            event_type_id: ID for the event to raise
        poller_result: dictionary:
            state - optional event AlarmState description
            other fields copied to event
        """
        self._run_event(attribute, poller_result, True)

    def _run_admin_status(self, poller_row, attribute, poller_result):
        """
        Backend: admin_status
        Set the admin_status of the attribute based upon the string
        that is given by the poller. The string must be one of the
        four known states (up, down, testing, unknown)
        """
        old_state = attribute.admin_state
        if attribute.set_admin_state(poller_result):
            if old_state == attribute.admin_state:
                return "Admin status not changed"
            else:
                return "Admin status set to {0}".format(poller_result)
        return "Bad Admin status \"{0}\"".format(poller_result)

    def _run_oper_status(self, poller_row, attribute, poller_result):
        """
        Backend: oper_status
        Set the oper_status of the attribute based upon the integer
        the backend receives from poller.
        poller parameters: None
        poller_result: integer
        """
        try:
            new_state = int(poller_result)
        except ValueError:
            return "Oper status received by poller is not a integer"
        if attribute.oper_state == poller_result:
            return "Oper status not changed."
        attribute.oper_state = poller_result
        return "Oper status set to "+str(poller_result)

    def _run_verify_index(self, poller_row, attribute, poller_result):
        """
        Backend: verify_index
        Update and set the index for this attribute if required.
        If the poller_result is None then it is unchanged
        """
        if poller_result is None:
            return 'not changed'
        try:
            new_index = str(poller_result)
        except ValueError:
            return 'Cannot convert poller_result to string'
        if poller_result == attribute.index:
            return 'not changed'
        old_index = attribute.index
        attribute.index = new_index
        return 'Changed {0} -> {1}'.format(old_index, new_index)

    def _backend_raise_event(self, attribute, event_type, alarm_state, damp_time):
        """
        Should the event backend raise an event?
        """
        if alarm_state.is_alert():
            return True # always raise alert level events

        down_alarm = Alarm.find_down(attribute,event_type)

        # Raise an up event if the down event was more that wait_time minutes ago
        if alarm_state.is_up() and down_alarm is not None:
            if datetime.datetime.now() > down_alarm.start_time + datetime.timedelta(minutes=damp_time):
                return True

        if alarm_state.is_downtesting():
            if down_alarm is None:
                return True
            else:
                if down_alarm.alarm_state != alarm_state:
                    return True
        return False 


