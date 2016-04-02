# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2011-2016 Craig Small <csmall@enc.com.au>
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
""" Database entries for the SLA models """
# name, text, atype,
#   expression, oper, limit, show_res, show_info,show_expr
OR_ROW = ('OR', u'=', 0, False, u'', u'', u'')

slas = (
    (u'Cisco Router', u'Router:', u'Cisco System Info', (
        ('$cpu - $cpu_threshold', u'>', 0, True,
            u'Usage > $cpu_threshold', u'$cpu', u'%'),
        ('$mem_used * 100 / ($mem_used + $mem_free)', u'>', 80, True,
            u'Memory Usage > 80%', u'$mem_used * 100 / '
            '($mem_used + $mem_free)', u'%'),
        OR_ROW
    )),
    (u'Linux/Unix CPU', u'', u'Linux/Unix System Info', (
        ('$load_average_5', u'>', 5, True,
            u'Load Average > 5', u'$load_average_5', u''),
        ('($cpu_user_ticks + $cpu_nice_ticks + $cpu_system_ticks) * 100 / '
         '($cpu_user_ticks + $cpu_idle_ticks + $cpu_nice_ticks + '
         '$cpu_system_ticks) - $cpu_threshold', u'>', 0, True,
         u'Usage > $cpu_threshold%',
         u'($cpu_user_ticks + $cpu_nice_ticks + $cpu_system_ticks) * 100 / '
         '($cpu_user_ticks + $cpu_idle_ticks + $cpu_nice_ticks + '
         '$cpu_system_ticks)', u'%'),
        OR_ROW
    )),
    (u'Windows CPU', u'', u'Windows System Info', (
        ('$cpu', u'>', 90, True,
            u'CPU > 90%', u'$cpu', u'%'),
        ('$num_procs - $proc_threshold', u'>', 0, True,
            u'Processes > $proc_threshold', u'$num_procs', u'Processes'),
        OR_ROW
    )),
    (u'Physical Interface', u'Interface:', u'Physical Interfaces', (
        ('$input * 100 / $speed', u'>', 90, True,
            u'IN > 90%', u'$input / 1000', u'kbps'),
        ('$output * 100 / $speed', u'>', 90, True,
            u'IN > 90%', u'$output / 1000', u'kbps'),
        ('$inerrors * 100 / ($inpackets + 1 )', u'>', 10, True,
            u'IN ERR > 20%', u'($inputerrors * 100) / ($inpackets + 1)',
            u'% = $inerrors Eps'),
    )),
    (u'Storage', u'Storage:', u'Storage', (
        ('$used_blocks * 100 / $total_blocks - $usage_threshold', u'>', 0,
            True,
            u'Used > $usage_threshold', u'($used_blocks * 100) / '
            '$total_blocks', u'%'),
    )),
)
