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


from rnms import model

__all__ = [ 'event', 'alarm', 'admin_status', 'oper_status', ]

def alarm(host, attribute, parameters, poller_result):
    """
    Backend: alarm
    Raises an event if required.
    poller parameters: <event_type_id>,[<default>],[<damp_time>]
      event_type_id: ID for the event to raise
      default:       if poller_result is nothing use this string
      damp_time:     time to wait before raising event
    poller_result: dictionary
      state - optional display_name to match AlarmState model
      info -  optional extra info
    """
    params = parameters.split(',')
    try:
        event_type_id = int(params[0])
    except ValueError:
        return "EventType ID \"{0}\" is not an integer.".format(params[0])
    event_type = model.EventType.by_id(event_type_id)
    if event_type is None:
        return "ID \"{0}\" is not found in EventType table.".format(even_type_id)
    if len(params) > 1:
        default_input = params[1]
    else:
        default_input = ''
    if len(params) > 2:
        damp_time = params[2]
    else:
        damp_time = 30

    if type(poller_result) is not dict:
        return 'Poller did not provide a dictionary type'
    if 'state' in poller_result:
        alarm_description = poller_result['state']
    elif default_input == '':
            alarm_description='down'
        elif default_input != 'nothing':
            alarm_description = default_input
    if 'info' in poller_result:
        event_info = poller_result['info']

    alarm_state = model.AlarmState.by_name(alarm_description)
    if alarm_state is None:
        return "Description \"{0}\" is not found in AlarmState table.".format(alarm_description)

    if backend_raise_event(attribute, event_type, alarm_state, wait_time):
        if event_info is not None:
            event_fields = {'info': event_info}
        else:
            event_fields=None
        new_event = model.Event(event_type=event_type, host=attribute.host,
                attribute=attribute, alarm_state=alarm_state,
                field_list=event_fields)
        DBSession.add(new_event)
        new_event.process()
        return "Event added: {0}".format(new_event.id)
    else:
        return "Nothing was done"

def event(host, attribute, parameters, poller_result):
    """
    Backend: event
    Unconditionally raise an event
    poller parameters: <event_type_id>
      event_type_id: ID for the event to raise
    poller_result: dictionary:
     info - optional info attribute
     state - optional event AlarmState description
    """
    try:
        event_type_id = int(parameters)
    except ValueError:
        return "EventType ID \"{0}\" is not an integer.".format(parameters)
    event_type = model.EventType.by_id(event_type_id)
    if event_type is None:
        return "ID \"{0}\" is not found in EventType table.".format(event_type_id)
    if type(poller_result) is not dict:
        return 'Poller did not provide a dictionary type'
    if 'state' in poller_result:
        alarm_description = poller_result['state']
        alarm_state = model.AlarmState.by_name(alarm_description)
    else:
        alarm=state = None
    if 'info' in poller_result:
        event_fields = {'info' : poller_result['info']}
    else:
        event_fields = None
    new_event = model.Event(event_type=event_type, host=host, attribute=attribute, alarm_state=alarm_state, fields=event_fields)
    DBSession.add(new_event)
    new_event.process()
    return "Inserted event ID {0}".format(new_event.id)

def admin_status(host, attribute, parameters, poller_result):
    """
    Backend: admin_status
    Set the admin_status of the attribute based upon the integer
    the backend receives from poller.
    poller parameters: None
    poller_result: integer
    """
    try:
        new_state = int(poller_result)
    except ValueError:
        return "Admin status received by poller is not a integer"
    if attribute.admin_state == poller_result:
        return "Admin status not changed."
    attribute.admin_state = poller_result
    return "Admin status set to "+str(poller_result)

def oper_status(host, attribute, parameters, poller_result):
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

###################################################
#
# Private funxtions
def backend_raise_event(attribute, event_type, alarm_state,wait_time):
    """
    Should the event backend raise an event?
    """
    if alarm_state.is_alert():
        return True # always raise alert level events

    down_alarm = model.Alarm.find_down(attribute,event_type)

    # Raise an up event if the down event was more that wait_time minutes ago
    if alarm_state.is_up() and down_alarm is not None:
        if datetime.datetime.now() > down.alarm.start_time + datetime.timedelta(minutes=wait_time):
            return True

    if alarm_state.is_downtesting():
        if down_alarm is None:
            return True
        else:
            if down_alarm.alarm_state != alarm_state:
                return True
   return False 


    event_type_id = int(parameters)
    new_event = model.Event()
    new_event.event_type = event_type_id
    new_event.host = host

