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
""" APC Discovery """
from rnms.lib import snmp
from rnms import model


def discover_apc(dobj, att_type, host):
    oids = (
            (1,3,6,1,4,1,318,1,1,1,1,1,1,0),
            (1,3,6,1,4,1,318,1,1,1,1,1,2,0),
            (1,3,6,1,4,1,318,1,1,1,2,1,1,0),
            )
    req = snmp.SNMPRequest(host)
    req.set_replyall(True)
    req.oid_trim = 4
    for oid in oids:
        req.add_oid(oid, cb_apc,
                    data={'dobj':dobj,'att_type':att_type,'host':host})
    return dobj.snmp_engine.get(req)

def cb_apc(values, error, host, dobj, att_type):
    if values is None or values['1.1.1.0'] is None:
        dobj.discover_callback(host.id, {})
    else:
        new_att = model.DiscoveredAttribute(host.id, att_type)
        new_att.display_name = unicode(values['1.1.1.0'])
        new_att.index = '1'
        new_att.set_field('description', unicode(values['1.1.2.0']))
        state = values['2.1.1.0']
        if state == 1 or state == 3:
            new_att.set_oper_down()
        dobj.discover_callback(host.id, {'1': new_att})

