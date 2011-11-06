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
""" Backend libraries """

from rnms import model

def alarm(host, attribute, parameters, poller_value):
    event_type_id = int(parameters)
    new_event = model.Event()
    new_event.event_type = event_type_id
    new_event.host = host

def event(host, attribute, parameters, poller_value):
    new_event = Event(int(poller_value), [])

def set_admin_status(host, attribute, parameters, poller_value):
    if attribute.admin_state == poller_value:
        return "Admin status not changed."
    attribute.admin_state = poller_value
    return "Admin status set to "+str(poller_value)

def set_oper_status(host, attribute, parameters, poller_value):
    if attribute.oper_state == poller_value:
        return "Oper status not changed."
    attribute.oper_state = poller_value
    return "Oper status set to "+str(poller_value)

