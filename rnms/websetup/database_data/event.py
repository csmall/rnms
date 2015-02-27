# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2011-2015 Craig Small <csmall@enc.com.au>
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
#
"""This file contains the database entries that are used for intially filling
the database"""
from rnms.lib import states
#Name, priority, down snd, up snd, int state, color
event_states = (
    (u'down', 10, 'down.wav', 'up.wav', states.STATE_DOWN, u'Down'),
    (u'up', 100, '', '', states.STATE_UP, u'Up'),
    (u'alert', 60, 'boing.wav', '', states.STATE_ALERT, u'Alert'),
    (u'testing', 40, '', '', states.STATE_TESTING, u'Testing'),
    (u'running', 100, '', '', states.STATE_UP, u'Up'),
    (u'not running', 20, '', '', states.STATE_DOWN, u'Down'),
    (u'open', 100, '', '', states.STATE_UP, u'Up'),
    (u'closed', 15, '', '', states.STATE_DOWN, u'Service'),
    (u'error', 90, 'boing.wav', '', states.STATE_ALERT, u'Alert'),
    (u'invalid', 30, '', '', states.STATE_DOWN, u'Service'),
    (u'valid', 110, '', '', states.STATE_UP, u'Service'),
    (u'reachable', 100, '', '', states.STATE_UP, u'Up'),
    (u'unreachable', 5, '', '', states.STATE_DOWN, u'Down'),
    (u'lowerlayerdown', 10, 'down.wav', 'up.wav', states.STATE_DOWN, u'Down'),
    (u'synchronized', 100, '', '', states.STATE_UP, u'Information'),
    (u'unsynchronized', 6, '', '', states.STATE_DOWN, u'Information'),
    (u'battery normal', 100, '', '', states.STATE_UP, u'Up'),
    (u'battery low', 4, '', '', states.STATE_DOWN, u'Alert'),
    (u'battery unknown', 2, '', '', states.STATE_UNKNOWN, u'Unknown'),
    (u'on battery', 3, '', '', states.STATE_DOWN, u'Alert'),
    (u'on line', 90, '', '', states.STATE_UP, u'Up'),
    (u'ok', 100, '', '', states.STATE_UP, u'Up'),
    (u'out of bounds', 10, '', '', states.STATE_DOWN, u'Down'),
    (u'unavailable', 10, 'down.wav', 'up.wav', states.STATE_DOWN, u'Down'),
    (u'available', 100, '', '', states.STATE_UP, u'Down'),
    (u'battery depleted', 3, '', '', states.STATE_DOWN, u'Fault'),
    (u'other', 10, '', '', states.STATE_DOWN, u'Fault'),
    (u'unknown', 10, '', '', states.STATE_UNKNOWN, u'Unknown'),
    (u'noncritical', 90, '', '', states.STATE_ALERT, u'Alert'),
    (u'critical', 10, '', '', states.STATE_DOWN, u'Down'),
    (u'nonrecoverabl', 10, '', '', states.STATE_DOWN, u'Fault'),
    (u'warning', 80, 'down.wav', 'up.wav', states.STATE_ALERT, u'Alert')
    )

event_types = (
    # display_name, tag, text, gen_alm, alm_dur, sh_host
    (u'Unknown', 'unknown', u'$attribute $state $info',
        False, 0, True),
    (u'Administrative', 'admin', u'$attribute $info',
        True, 1800, True),
    (u'SLA', 'sla', u'$attribute $info (${client} ${description})',
        True, 1800, True),
    (u'Internal', 'internal', u'$user $attribute $state $info',
        False, 0, False),
    (u'BGP Status', 'bgp_status',
        u'BGP Neighbor $attribute $state $info (${client} ${description})',
        True, 0, True),
    (u'BGP Notification', 'bgp_notify',
        u'Notification $direction $attribute ($info)',
        False, 0, True),
    (u'TCP/UDP Service', 'tcpudp_service',
        u'TCP/UDP Service $attribute $state (${client} ${description}) $info',
        True, 0, True),
    (u'TCP Content', 'tcp_content',
        u'Content Response on $attribute is $state (${client} ${description})'
        '$info',
        True, 0, True),
    (u'Configuration', 'configuration',
        u'$user changed configuration from $source',
        False, 0, True),
    (u'Interface Protocol', 'interface_protocol',
        u'Interface $attribute Protocol $state $info '
        '(${client} ${description})',
        True, 0, True),
    (u'Interface Link', 'interface_link',
        u'Interface $attribute Link $state $info (${client} ${description})',
        False, 0, True),
    (u'Controller Status', 'controller_status',
        u'Controller  $info $attribute $state',
        False, 0, True),
    (u'Interface Shutdown', 'interface_shutdown',
        u'Interface $attribute $info $state (${client} ${description})',
        False, 0, True),
    (u'Clear Counters', 'clear_counters',
        u'<user> Cleared Counters of $attribute  (${client} ${description})',
        False, 0, True),
    (u'Environmental', 'environment', u'$attribute $state $info',
        True, 0, True),
    (u'Duplex Mismatch', 'duplex_mismatch',
        u'Duplex Mismatch, $attribute is ${our_dup} and ${their_int} is'
        '${their_dup}',
        False, 0, True),
    (u'ACL', 'acl',
        u'ACL $attribute $state $info packets from <user>',
        False, 0, True),
    (u'Excess Collisions', 'collision',
        u'Excess Collisions on Interface $attribute',
        False, 0, True),
    (u'Application', 'application',
        u'Application $attribute is $state $info (${client} ${description})',
        True, 0, True),
    (u'Reachability', 'reachability', u'Host is $state with $info',
        True, 0, True),
    (u'NTP', 'ntp', u'$attribute is $state $info',
        True, 0, True),
    (u'APC Status', 'apc_status', u'$attribute is $state $info',
        True, 0, True),
    (u'Alteon RServer', 'alteon_rserver', u'Real Server $attribute is $state',
        True, 0, True),
    (u'Alteon Service', 'alteon_service',
        u'Real Service $attribute is $state $info',
        True, 0, True),
    (u'Alteon VServer', 'alteon_vserver',
        u'Virtual Server $attribute is $state $info',
        False, 0, True),
    (u'Brocade FC Port', 'brocade_fcport',
        u'$attribute $state ($info)',
        True, 0, True),
    (u'OS/400 Error', 'os400_error',
        u'A subsystem is $state on the OS/400',
        True, 0, True),
    (u'Storage Controller', 'storage_controller', u'$info',
        True, 0, True)
    )

severities = (
    (u'Up', '00ff00', '000000'),
    (u'Down', 'ff0000', 'ffffff'),
    (u'Testing', 'f9fd5f', '000000'),
    (u'Unknown',        '000000', 'ffffff'),
    (u'Alert',        '00aa00', 'ffffff'),
    (u'Big Fault',      'da4725', 'ffffff'),
    (u'Fault',          'f51d30', 'eeeeee'),
    (u'Service',        '0090f0', 'ffffff'),
    (u'Information',    'f9fd5f', '000000'),
    (u'Administrative', '8d00ba', 'ffffff'),
    )

triggers = (
    (u'Interface Status Change', False, True, u'${attribute} ${state}',
     u'The attribute ${attribute} is ${state} on host ${host}.', (
         ('event_type', '!IN', 'sla,admin', False, False),
     )),
)
