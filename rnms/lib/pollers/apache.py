# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012,2013 Craig Small <csmall@enc.com.au>
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

response_re = re.compile('([A-Z][ A-Za-z]+): ([0-9.]+)\s')
return_fields = ('Total Accesses', 'Total kBytes', 'CPULoad', 'Uptime', 'BytesPerReq', 'BusyWorkers', 'IdleWorkers')

def poll_apache(poller_buffer, parsed_params, **kw):
    return kw['pobj'].tcp_client.get_tcp(kw['attribute'].host, 80, 'GET /server-status?auto HTTP/1.1\r\nHost: {}\r\n\r\n'.format(kw['attribute'].host.mgmt_address), 1000, cb_apache, **kw)

def cb_apache(host, response, connect_time, error, pobj, poller_row, attribute, **kwargs):
    if response is not None and response[:15] == 'HTTP/1.1 200 OK':
        match = response_re.findall(response)
        if match is not None:
            retvals = [0 for x in return_fields]
            for k,v in match:
                try:
                    idx = return_fields.index(k)
                except ValueError:
                    pass
                else:
                    retvals[idx] = v
            pobj.poller_callback(attribute.id, poller_row, retvals)
            return
    pobj.poller_callback(attribute.id, poller_row, None)


