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
# This poller is based upon the JFFNMS poller of the same name
# Copyright (C) <2002-2005> Javier Szyszlican <javier@szysz.com>

# For details on setting ip accounting up see
# http://www.cisco.com/en/US/tech/tk648/tk362/technologies_configuration_example09186a0080094aa2.shtml

import logging

from rnms.lib import snmp

def poll_cisco_accounting(poller_buffer, parsed_params, **kw):
    """
    Step #1: Get the accounting checkpoint id
    """
    oid = (1,3,6,1,4,1,9,2,4,11,0)
    if kw['attribute'].host.community_rw is None:
        kw['pobj'].poller_callback(kw['attribute'].id, kw['poller_row'], None)
        return True

    kw['pobj'].snmp_engine.get_int(kw['attribute'].host, oid, set_acct_checkpoint, **kw)
    return True

def set_acct_checkpoint(value, error, **kw):
    """
    Step 2
    Set the checkpoint value back to device, this then enables the
    accounting table
    """
    oid = (1,3,6,1,4,1,9,2,4,11,0)
    if value is None:
        kw['pobj'].poller_callback(kw['attribute'].id, kw['poller_row'], None)

    kw['checkpoint'] = int(value)
    req = snmp.SNMPRequest(kw['attribute'].host)
    req.add_oid(oid, get_acct_table, data=kw, value=int(value))
    kw['pobj'].snmp_engine.set(req)

def get_acct_table(value, error, **kw):
    """
    Step 3: Actually fetch the accounting table
    """
    oid = (1,3,6,1,4,1,9,2,4,9)
    kw['pobj'].snmp_engine.get_table(kw['attribute'].host, oid, cb_acct_table, **kw)

def cb_acct_table(value, error, pobj, attribute, poller_row, **kw):
    # FIXME - does anyone use this? is it required?
    pobj.poller_callback(attribute.id, poller_row, (0,0))