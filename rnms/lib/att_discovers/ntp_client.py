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
""" Discover NTP clients """
from rnms import model

def discover_ntp_client(host, **kw):
    return kw['dobj'].ntp_client.get_peers(host, cb_ntp_peer_list, **kw)

def cb_ntp_peer_list(host, ntp_response, dobj, att_type, **kw):
    if ntp_response is None or ntp_response.peers == []:
        dobj.discover_callback(host.id, {})
        return
    new_att = model.DiscoveredAttribute(host.id, att_type)
    new_att.display_name = u'Time'
    new_att.index = '1'
    for assoc in ntp_response.peers:
        if assoc.selection == 6: # found a synchronised
            break
    else:
        new_att.oper_state = 2
    dobj.discover_callback(host.id, {'1': new_att})

