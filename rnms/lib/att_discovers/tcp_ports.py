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
""" Discover TCP ports by running nmap """
import logging
import re
import os

from rnms import model

logger = logging.getLogger('rnms')
nmap_bin = '/usr/bin/nmap'
nmap_bin_ok =  os.access(nmap_bin, os.X_OK)

port_re = re.compile(r'\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*$')

def discover_tcp_ports(host, **kw):
    ports = kw['att_type'].ad_parameters
    return kw['dobj'].nmap_client.scan_host(host, cb_tcp_ports, ports, host=host, **kw)

def cb_tcp_ports(values, error, host, dobj, att_type, **kw):
    tcp_ports = {}
    for port_info in values:
        if len(port_info) < 4 or port_info[1] != 'open':
            continue
        port_num = port_info[0].strip()
        new_port = model.DiscoveredAttribute(host.id, att_type)
        new_port.display_name = 'Port {}'.format(port_num)
        new_port.index = port_num
        new_port.set_field('description', port_info[4])
        tcp_ports[port_num] = new_port
    dobj.discover_callback(host.id, tcp_ports)

