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
import re

def poll_tcp_status(poller_buffer, parsed_params, **kwargs):
    """
    Connect to the remote server on a port and collect some of the
    data for later processing.
    Poller parameters: <bytes>
      bytes = bytes to gather, 0 means all, usually 1 gets first line
    Poller Returns: <status>|<data>|<connect_time>
      state = open or closed
      data = data from server
      connect_time = how long it took to connect
    """
    port = int(kwargs['attribute'].index)
    try:
        max_bytes = int(parsed_params)
    except ValueError:
        max_bytes = 1
    if kwargs['attribute'].get_field('check_content') != '1':
        max_bytes = None

    return kwargs['pobj'].tcp_client.get_tcp(kwargs['attribute'].host, port, ' ', max_bytes, cb_tcp_status, **kwargs)

def cb_tcp_status(values, error, pobj, attribute, poller_row, **kwargs):
    """
    Callback for tcp_status. Store the content for later
    """
    connect_time = values[1]
    if error is None:
        state = u'open'
        tcp_error = None
    else:
        state = u'closed'
        tcp_error = error[1]
    
    response = values[0].rstrip()
    if values[1] is not None:
        connect_time = values[1].total_seconds()

    pobj.poller_callback(attribute.id, poller_row,(state, response, connect_time, tcp_error))
        
def poll_snmp_tcp_established(poller_buffer, parsed_params, **kw):
    """
    Get the  tcp.tcpConnTable.tcpConnEntry.tcpConnState SNMP table
    to find the number of established TCP connections for the given
    port
    """
    oid = (1,3,6,1,2,1,6,13,1,1)
    kw['pobj'].snmp_engine.get_table(kw['attribute'].host, (oid,), cb_snmp_tcp_established, **kw)
    return True

def cb_snmp_tcp_established(values, error, pobj, attribute, poller_row, **kw):
    if values is None:
        pobj.poller_callback(attribute.id, poller_row, None)
        return

    port = str(attribute.index)
    est_count = 0
    for oid,val in values[0].items():
        if val == '5' and oid.split('.')[-6] == port:
            est_count += 1

    pobj.poller_callback(attribute.id, poller_row, est_count)

def poll_tcp_content(poller_buffer, parsed_params, pobj, attribute, poller_row, **kw):
    """
    Check tcp_content poller buffer for matches
    Requires tcp_content from poller buffer as the string matched against
    Attribute fields: 
      check_content: 1 to run this check
      check_regexp: PCRE pattern used for matching
    """

    if attribute.get_field('check_content') != '1':
        pobj.poller_callback(attribute.id, poller_row, [u'valid', u'not checked'])
        return True

    try:
        data = poller_buffer['tcp_content']
    except KeyError:
        pobj.poller_callback(attribute.id, poller_row, [u'invalid', u'missing buffer'])
        return True
    if data == '':
        pobj.poller_callback(attribute.id, poller_row, [u'invalid', u'no data'])
        return True

    try:
        regex = re.compile(attribute.get_field('check_regexp'), re.I)
    except re.error:
        pobj.poller_callback(attribute.id, poller_row, [u'invalid', u'bad regexp configured'])
        return True

    if regex.find(data) is not None:
        pobj.poller_callback(attribute.id, poller_row, [u'valid', unicode(data[:40])])
    else:
        pobj.poller_callback(attribute.id, poller_row, u'invalid')


    return False
