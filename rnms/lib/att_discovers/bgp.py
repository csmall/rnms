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
""" Discover BGP peers using RFC 1269 MIB information """

from rnms import model

def discover_bgp_peers(dobj, att_type, host):
    table_oid = (1,3,6,1,2,1,15,3,1)
    columns = (1,2,5,7,9)
    oids = tuple([table_oid + (col,) for col in columns])
    return dobj.snmp_engine.get_table(
        host, oids, cb_bgp_peers, table_trim=4,
        host=host, dobj=dobj, att_type=att_type)

def cb_bgp_peers(values, error, host, dobj, att_type):
    bgp_peers = {}
    if values is None:
        dobj.discover_callback(host.id, bgp_peers)
        return

    for remote_addr in values[3].values():
        new_peer = model.DiscoveredAttribute(host.id, att_type)
        new_peer.display_name = remote_addr
        new_peer.index = remote_addr
        if values[1][remote_addr] != '6':
            new_peer.oper_state = 2
        new_peer.set_field('local', unicode(values[2][remote_addr]))
        new_peer.set_field('asn', u'AS ' + unicode(values[4][remote_addr]))
        bgp_peers[remote_addr] = new_peer
    dobj.discover_callback(host.id, bgp_peers)

