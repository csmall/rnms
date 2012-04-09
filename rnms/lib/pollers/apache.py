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
import httplib

def run_apache(poller, attribute, poller_buffer):
    hostname = attribute.get_field('hostname')
    if hostname is None:
        return None
    conn = httplib.HTTPConnection(hostname)
    conn.request("GET", "/server-status?auto")
    resp = conn.getresponse()
    #r1.status sghould be 200
    response_data = r1.read()
    for line in response_data.split('\n'):
        pass #FIXME
    conn.close()


