# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012-2014 Craig Small <csmall@enc.com.au>
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
"""
Poller and SNMP trap backends
 All backends have the same set of arguments
   host          - Host that the attribute was polled for
   attribute     - Attribute that was polled
   parameters    - The parameters column from Backend model
   poller_result - Output from the poller

 poller_result can either be a string or a dictionary.

 Backends should return a string that describes the status. This
 string appears in the logs.
"""
import datetime

from rnms.model import DBSession, EventType, Event, EventState


class CacheBackend(object):
    backend_function = None
    parameters = None
    display_name = None

    def __init__(self, db_backend):
        self.display_name = db_backend.display_name
        self.parameters = db_backend.parameters.split(',')
        self.set_command(db_backend.command)

    def enabled(self):
        """ Return true if backend is enabled, ie there is something to do """
        return self.backend_function is not None

    def set_command(self, command):
        """ Set the command used for backend """
        if command is None or command in ('none', ''):
            self.backend_function = None
        else:
            try:
                self.backend_function = \
                    getattr(self, "_run_"+command)
            except AttributeError:
                raise ValueError("Backend Plugin \"{}\" not found for {}".
                                 format(command,
                                        self.display_name))

    def run(self, poller_row, attribute, poller_result):
        """
        Run the real backend method "_run_BLAH" based upon the command
        used
        """
        if self.backend_function is None:
            return ''
        return self.backend_function(poller_row, attribute, poller_result)

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

        event_type = EventType.by_tag(self.parameters[0])
        if event_type is None:
            return "Tag \"{0}\" is not found in EventType table.".\
                format(self.parameters[0])
        try:
            default_input = self.parameters[1]
        except IndexError:
            default_input = ''

        try:
            damp_time = int(self.parameters[2])
        except (IndexError, ValueError):
            damp_time = 1

        if default_input == '':
            event_state_name = 'down'
        elif default_input != 'nothing':
            event_state_name = default_input

        event_fields = {}
        if type(poller_result) in (list, tuple):
            event_state_name = poller_result[0]
            try:
                event_fields['info'] = poller_result[1]
            except IndexError:
                pass  # no additional info
        elif type(poller_result) is dict:
            try:
                event_state_name = poller_result['state']
            except KeyError:
                pass
            event_fields = {k: v for k, v in poller_result.items()
                            if k != 'state'}
        else:
            event_state_name = poller_result
        if event_state_name is None:
            return "Poller returned None, nothing done"

        event_state = EventState.by_name(event_state_name)
        if event_state is None:
            return "Description \"{0}\" is not found in EventState table.".\
                format(event_state_name)

        if always or self._backend_raise_event(attribute, event_type,
                                               event_state, damp_time):
            new_event = Event(
                event_type=event_type,
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

    def _backend_raise_event(self, attribute, event_type, event_state,
                             damp_time):
        """
        Should the event backend raise an event?
        """
        if event_state.is_alert():
            return True  # always raise alert level events

        down_event = Event.find_down(attribute.id, event_type.id)

        # Raise an up event if the down event was more that wait_time
        # minutes ago
        if event_state.is_up() and down_event is not None:
            if datetime.datetime.now() >\
                    down_event.created + datetime.timedelta(minutes=damp_time):
                return True

        if event_state.is_downtesting():
            if down_event is None:
                return True
            else:
                if down_event.event_state != event_state:
                    return True
        return False
