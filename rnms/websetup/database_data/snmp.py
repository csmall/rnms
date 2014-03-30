# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011-2014 Craig Small <csmall@enc.com.au>
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
    (0, 'ifTable Link Down', '1.3.6.1.6.3.1.1.5.3',
        'match_index', '1.3.6.1.2.1.2.2.1.1.5',
        'fixed', 'down',
        u'Alarm Verify Operational', False),
    (0, 'ifTable Link Up', '1.3.6.1.6.3.1.1.5.4',
        'match_index', '1.3.6.1.2.1.2.2.1.1.5',
        'fixed', 'up',
        u'Alarm Verify Operational', False),
    )
