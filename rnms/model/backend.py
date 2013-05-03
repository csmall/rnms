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

from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode, String
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, DBSession, EventType, EventState, Event


class Backend(DeclarativeBase):
    """
    Poller and SNMP trap backends
    The backend is used for pollers and for trap receivers and generally
    is used to raise events or to set something in the database.

    All backends have the same set of arguments:
        attribute     - Attribute that was polled
        poller_result - Output from the poller. Can be string or
          dictionary but its the same for same backend type.
    Backends should return a string that describes the status. This
    string appears in the logs.
    """
    __tablename__ = 'backends'

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
        try:
            real_backend = getattr(self, "_run_"+self.command)
        except AttributeError:
            return 'invalid backend {0}'.format(self.command)
        else:
            return real_backend(poller_row, attribute, poller_result)

    def _run_event(self, poller_row, attribute, poller_result, always=False):
        """
        Backend: event
        Raises an event if required.
        poller parameters: <event_type_tag>,[<default>],[<damp_time>]
        event_type_tag: tag used to find the correct EventType
        default:       if poller_result is nothing use this string
        damp_time:     time to wait before raising event
        poller_result: dictionary or (state,info) tuple
           state - optional display_name to match EventState model
           other items are copied into event fields

        """

        params = self.parameters.split(',')
        event_type = EventType.by_tag(params[0])
        if event_type is None:
            return "Tag \"{0}\" is not found in EventType table.".format(params[0])
        try:
            default_input = params[1]
        except IndexError:
            default_input = ''

        try:
            damp_time = int(params[2])
        except (IndexError, ValueError):
            damp_time = 1

        if default_input == '':
            event_state_name='down'
        elif default_input != 'nothing':
            event_state_name = default_input

        event_fields={}
        if type(poller_result) is list:
            event_state_name = poller_result[0]
            try:
                event_fields['info'] = poller_result[1]
            except IndexError:
                pass # no additional info
        elif type(poller_result) is dict:
            try:
                event_state_name = poller_result['state']
            except KeyError:
                pass
            event_fields = {k:v for k,v in poller_result.items() if k!='state'}
        else:
            event_state_name = poller_result

        event_state = EventState.by_name(event_state_name)
        if event_state is None:
            return "Description \"{0}\" is not found in EventState table.".format(event_state_name)

        if always==True or self._backend_raise_event(attribute, event_type, event_state, damp_time):
            new_event = Event(event_type=event_type, 
                    attribute=attribute, event_state=event_state,
                    field_list=event_fields)
            DBSession.add(new_event)
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
            state - optional event EventState description
            other fields copied to event
        """
        return self._run_event(attribute, poller_result, True)

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

    def _backend_raise_event(self, attribute, event_type, event_state, damp_time):
        """
        Should the event backend raise an event?
        """
        if event_state.is_alert():
            return True # always raise alert level events

        down_event = Event.find_down(attribute.id,event_type.id)

        # Raise an up event if the down event was more that wait_time minutes ago
        if event_state.is_up() and down_event is not None:
            if datetime.datetime.now() > down_event.start_time + datetime.timedelta(minutes=damp_time):
                return True

        if event_state.is_downtesting():
            if down_event is None:
                return True
            else:
                if down_event.event_state != event_state:
                    return True
        return False


