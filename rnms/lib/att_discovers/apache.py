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
from rnms.model.attribute import DiscoveredAttribute


def discover_apache(host, **kw):
    """
    Make a http call to the host to see if we get the apache status screen
    """
    return kw['dobj'].tcp_client.get_tcp(host, 80, 'GET /server-status?auto HTTP/1.1\r\nHost: {0}\r\n\r\n'.format(host.mgmt_address), 40, cb_apache, **kw)

def cb_apache(values, error, host, dobj, att_type, **kw):
    # values is (response, connect_time)
    if values is None or len(values) != 2:
        dobj.discover_callback(host.id, {})
        return
    if type(values[0]) is not str:
        dobj.discover_callback(host.id, {})
        return
    response = values[0]

    if len(response) > 15 and response[:15] == 'HTTP/1.1 200 OK':
        apache_att = DiscoveredAttribute(host.id, att_type)
        apache_att.display_name = u'Apache Information'
        apache_att.index = '{}:80'.format(host.mgmt_address)
        dobj.discover_callback(host.id, {apache_att.index: apache_att})
    else:
        dobj.discover_callback(host.id, {})
    
