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
""" SNMP related database information """
snmp_communities = (
    (u'None', 1, ''),
    (u'v1 Default', 1, 'public'),
    (u'v2c Default', 2, 'public'),
)

trap_matches = (
    (0, u'ifTable Link Down', '1.3.6.1.6.3.1.1.5.3',
        u'Physical Interfaces',
        u'match_index', u'1.3.6.1.2.1.2.2.1.1.5', (
            ('state', 'fixed', 'down'),
        ),
        u'Alarm Verify Operational', False),
    (0, u'ifTable Link Up', '1.3.6.1.6.3.1.1.5.4',
        u'Physical Interfaces',
        u'match_index', u'1.3.6.1.2.1.2.2.1.1.5', (
            ('state', 'fixed', 'down'),
        ),
        u'Alarm Verify Operational', False),
    (0, u'Juniper Config Change', '1.3.6.1.4.1.2636.4.5.1',
        u'Reachable',  # FIXME - should be a Juniper CPU
        'first', '', (
            ('state', 'fixed', 'alert'),
            ('user', 'oid', '1.3.6.1.4.1.2636.3.18.1.7.1.5'),
            ('source', 'oid_map',
             '1.3.6.1.4.1.2636.3.18.1.7.1.4|2=cli,3=junoscript,'
             '5=snmp,6=button,7=autoinstall|unknown')
        ),
        u'Alarm Configuration', False),
    )
