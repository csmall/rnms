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
import logging

logger = logging.getLogger('CiscoPing')

def poll_cisco_snmp_ping_start(poller_buffer, **kwargs):
    """
    """
    logger.debug('Cisco Ping not implemented')
    kwargs['pobj'].poller_callback(kwargs['attribute'], None)
    return True

def poll_cisco_snmp_ping_wait(poller_buffer, **kwargs):
    poll_cisco_snmp_ping_start(poller_buffer, **kwargs)

def poll_cisco_snmp_ping_get_rtt(poller_buffer, **kwargs):
    poll_cisco_snmp_ping_start(poller_buffer, **kwargs)

def poll_cisco_snmp_ping_get_pl(poller_buffer, **kwargs):
    poll_cisco_snmp_ping_start(poller_buffer, **kwargs)

def poll_cisco_snmp_ping_end(poller_buffer, **kwargs):
    poll_cisco_snmp_ping_start(poller_buffer, **kwargs)

