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
from rnms.model import AttributeField

def poll_reach_ping(poller_buffer, parsed_params, **kw):
    """
    Poller that starts off the ping process
    Parameters: none
    Returns: rtt,pl
    """
    try:
        num_pings = int(AttributeField.field_value(kw['attribute'].id, 'pings'))
    except (TypeError, ValueError):
        num_pings = 10
    try:
        interval = int(AttributeField.field_value(kw['attribute'].id, 'interval'))
    except (TypeError, ValueError):
        interval = 300
    kw['pings'] = num_pings
    return kw['pobj'].ping_client.ping_host(kw['attribute'].host.mgmt_address, cb_reach_ping, num_pings, interval, **kw)

def cb_reach_ping(values, error, pobj, attribute, poller_row, **kw):
    pobj.poller_callback(attribute.id, poller_row, values)


def poll_reach_status(poller_buffer, parsed_params, pobj, attribute, poller_row, **kw):
    """"
    Poller that checks the value of the packet loss
    Expects 'pl' field from poller buffer which is packetloss percent
    Attribute Field: threshold which is the percent that triggers and event
    Returns: <state>,<info>

    """
    try:
        thres = int(AttributeField.field_value(attribute.id, 'threshold'))
    except (TypeError, ValueError):
        thres = 90

    loss = int(poller_buffer['pl'])
    result = u'reachable'
    if loss > thres:
        result = u'unreachable'
    pobj.poller_callback(attribute.id, poller_row, {'state': result, 'info':u'{0}% Packet loss'.format(loss)})
    return True
