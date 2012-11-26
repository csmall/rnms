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
""" Apache status autodiscovery """
import re


def discover_apache(host, **kw):
    """
    Make a http call to the host to see if we get the apache status screen
    """
    return kw['dobj'].tcp_client.get_tcp(host, 80, 'GET /server-status?auto HTTP/1.1\r\nHost: {0}\r\n\r\n'.format(host.mgmt_address), 40, cb_apache, **kw)

def cb_apache(host, response, connect_time, error, **kw):
    if type(response) is not str:
        kw['dobj'].discover_callback(host.id, [])
        return
    if r'HTTP\/1.1 200 OK' in response:
        #do something
        apache_att = DiscoveredAttribute(host.id, kw['att_type'].id)
        apache_att.display_name = u'Apache Information'
        kw['dobj'].discover_callback(host.id, [apache_att,])
    kw['dobj'].discover_callback(host.id, [])
    
