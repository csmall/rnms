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

    return kwargs['pobj'].tcp_client.get_tcp(kwargs['attribute'].host, port, '', max_bytes, cb_tcp_status, **kwargs)

def cb_tcp_status(host, response, connect_time, error, **kwargs):
    """
    Callback for tcp_status. Store the content for later
    """
    response = response.rstrip()
    if error is None:
        state = 'open'
        tcp_error = None
    else:
        state = 'closed'
        tcp_error = error[1]
    kwargs['pobj'].poller_callback(kwargs['attribute'].id, kwargs['poller_row'],(state, response, connect_time, tcp_error))
        
