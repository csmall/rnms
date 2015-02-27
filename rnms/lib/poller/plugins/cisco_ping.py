# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
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
"""
  Cisco ping implementation.
  http://www.cisco.com/en/US/tech/tk648/tk362/technologies_tech_note09186a0080094e8e.shtml

  Permits devices with snmp read/write community to ping remote devices
"""

from rnms.lib.snmp import SNMPRequest

# Define the OIDs
ciscoPingEntry = (1,3,6,1,4,1,9,9,16,1,1,1)
ciscoPingEntryStatus = ciscoPingEntry + (16,)

def set_ping_status(index, status, cb_fun, **kw):
    """
    Set the status of the ping entry
    """
    oid = ciscoPingEntryStatus + (int(index),)
    req = SNMPRequest(kw['attribute'].host)
    req.add_oid(oid, cb_fun, data=kw, value=int(status))
    kw['pobj'].snmp_engine.set(req)

    kw['pobj'].snmp_engine.get_int(kw['attribute'].host, oid, cb_fun, **kw)

def get_ping_status(index, cb_fun, **kw):
    """
    Get the status of the ping entry
    """
    oid = ciscoPingEntryStatus + (int(index),)
    kw['pobj'].snmp_engine.get_int(kw['attribute'].host, oid, cb_fun, **kw)


def poll_cisco_snmp_ping_start(poller_buffer, **kwargs):
    """
    """
    kwargs['pobj'].poller_callback(kwargs['attribute'].id, None)
    return True

def poll_cisco_snmp_ping_wait(poller_buffer, **kwargs):
    return poll_cisco_snmp_ping_start(poller_buffer, **kwargs)

def poll_cisco_snmp_ping_get_rtt(poller_buffer, **kwargs):
    return poll_cisco_snmp_ping_start(poller_buffer, **kwargs)

def poll_cisco_snmp_ping_get_pl(poller_buffer, **kwargs):
    return poll_cisco_snmp_ping_start(poller_buffer, **kwargs)

def poll_cisco_snmp_ping_end(poller_buffer, **kwargs):
    return poll_cisco_snmp_ping_start(poller_buffer, **kwargs)

