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
import logging

logger = logging.getLogger('pReach')

def poll_reach_ping(poller_buffer, parsed_params, **kw):
    """
    Poller that starts off the ping process
    Parameters: none
    Returns: rtt,pl
    """
    fields =  kw['attribute'].get_fields()
    try:
        num_pings = int(fields['pings'])
    except ValueError:
        num_pings = 10
    try:
        interval = int(fields['interval'])
    except ValueError:
        interval = 300
    kw['pings'] = num_pings
    return kw['pobj'].ping_client.ping_host(kw['attribute'].host, cb_reach_ping, num_pings, interval, **kw)

def cb_reach_ping(value, error, pobj, attribute, poller_row, **kw):
    pobj.poller_callback(attribute.id, poller_row, value)


def poll_reach_status(poller_buffer, parsed_params, pobj, attribute, poller_row, **kw):
    """"
    Poller that checks the value of the packet loss
    Expects 'pl' field from poller buffer which is packetloss percent
    Attribute Field: threshold which is the percent that triggers and event
    Returns: <state>,<info>

    """
    try:
        thres = int(attribute.field('threshold'))
    except ValueError:
        thres = 90

    loss = int(poller_buffer['pl'])
    result = u'reachable'
    if loss > thres:
        result = u'unreachable'
    pobj.poller_callback(attribute.id, poller_row, {'state': result, 'info':u'{0}% Packet loss'.format(loss)})
    return True
