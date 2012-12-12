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
""" Discover reachability (ping) """
from rnms import model

def discover_reachability(host, dobj, att_type, **kw):
    if dobj.ping_client.get_fping(host) is None:
        dobj.discover_callback(host.id, {})
    else:
        new_att = model.DiscoveredAttribute(host.id, att_type)
        new_att.display_name = 'Reachability to {}'.format(host.mgmt_address)
        new_att.index = '1'
        dobj.discover_callback(host.id, {'1': new_att})
    return True
