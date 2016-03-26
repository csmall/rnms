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
""" Database fields for attribute related models """
# showable 2=1, 0 1=1, 1 0=0, 0
# RRD Types = 1:gauge, 2:counter, 3:absolute
DS_GAUGE = 1
DS_COUNTER = 2
DS_ABSOLUTE = 3

attribute_types = (
    (u'No Interface Type',
        'none', '', False, False,
        u'No Polling', '', '',
        'AVERAGE', 103680, False, False, '',
        [], []),
    (u'TCP Ports',
        'tcp_ports', '500, 600-1024', False, True,
        u'TCP/IP Port', '', '',
        'LAST', 103680, True, True, '', (
            (u'Port Number', 'port', False, True, True, True, False,
                '0', '', ''),
            (u'Check Content', 'check_content', False, True, False, True, False,
                '0', '', ''),
            (u'Check Content URL', 'check_url', False, True, True, False, True,
                '', '', ''),
            (u'Check Content RegExp', 'check_regexp', False, True, False, True,
                False, '', '', '')
        ), (
            (u'Established Connections', 'tcp_established', 0, 0, 10000, 0),
            (u'Connection Delay', 'conn_delay', 0, 0, 10000, 0),
        )),
    (u'Cisco System Info',
        'host_information', 'cisco, 9.1, 9.5', True, True,
        u'Cisco Router', '', '',
        'AVERAGE', 103680, False, False, 'ent.9', (
            (u'Number of Processors', 'cpu_num', False, True, True, True, False,
                '1', '', ''),
            (u'CPU Usage Threshold', 'cpu_threshold', False, True, False, True,
                False, '60', '', ''),
            (u'System Name', 'name', True, True, True, True, False,
                '', '', ''),
            (u'Location', 'location', True, True, True, True, False,
                '', '', ''),
            (u'Contact', 'contact', True, True, True, True, False, '', '', ''),
        ), (
            (u'CPU', 'cpu', 0, 0, 100, ''),
            (u'Mem Used', 'mem_used', 0, 0, 100000000000, ''),
            (u'Mem Free', 'mem_free', 0, 0, 100000000000, ''),
            (u'Acct Packets', 'acct_packets', 2, 0, 100000000000, ''),
            (u'Acct Bytes', 'acct_bytes', 0, 0, 100000000000, ''),
            (u'TCP Active', 'tcp_active', 1, 0, 10000000, ''),
            (u'TCP Passive', 'tcp_passive', 1, 0, 10000000, ''),
            (u'TCP Established', 'tcp_established', 1, 0, 10000000, ''),
        )),
    (u'Physical Interfaces',
        'snmp_interfaces', '', True, True,
        u'SNMP Interface', '', '',
        'AVERAGE', 103680, True, False, '.', (
            (u'IP Address', 'address', True, True, True, True, False, False,
                '', ''),
            (u'IP Mask', 'mask', False, True, True, True, False, '', '', ''),
            (u'Peer Address', 'peer', False, True, True, True, False,
                '', '', ''),
            (u'Speed', 'speed', False, True, True, True, False, 1, '', ''),
            (u'Percentile', 'percentile', False, True, False, True, False,
             '', '', ''),
            (u'Flip In Out in Graphs', 'flipinout', False, True, True, True,
                False, 0, '', ''),
            (u'Pings to Send', 'pings', False, True, True, True, False,
                50, '', ''),
            (u'Fixed Admin Status', 'fixed_admin_status', False, True, True,
                True, False, 0, '', '')
        ), (
            (u'Input Bytes', 'input', 1, 0, 0, 'speed'),
            (u'Output Bytes', 'output', 1, 0, 0, 'speed'),
            (u'Input Errors', 'inputerrors', 1, 0, 0, 'speed'),
            (u'Output Errors', 'outputerrors', 1, 0, 0, 'speed'),
            (u'Round Trip Time', 'rtt', 0, 0, 10000, ''),
            (u'Packet Loss', 'packetloss', 0, 0, 1000, ''),
            (u'Input Packets', 'inpackets', 1, 0, 0, 'speed'),
            (u'Output Packets', 'outpackets', 1, 0, 0, 'speed'),
            (u'Drops', 'drops', 1, 0, 0, 'speed'),
        )),
    (u'BGP Neighbors',
        'bgp_peers', '', True, True,
        u'BGP Neighbor', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Local IP', 'local', True, True, True, False, True,
                False, '', ''),
            (u'Remote IP', 'remote', False, True, True, False, False,
                False, '', ''),
            (u'Autonomous System', 'asn', True, True, True, False, True,
                False, '', ''),
        ), (
            (u'BGP In Updates', 'bgpin', 1, 0, 10000000, ''),
            (u'BGP Out Updates', 'bgpout', 1, 0, 10000000, ''),
            (u'BGP Uptime', 'bgpuptime', 0, 0, 10000000, ''),
            (u'Accepted Routes', 'accepted_routes', 0, 0, 9000000, ''),
            (u'Advertised Routes', 'advertised_routes', 0, 0, 9000000, ''),
        )),
    (u'Storage',
        'storage', '', True, True,
        u'Storage Device', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Disk Type', 'storage_type', True, True, True, False, False,
                False, '', ''),
            (u'Size (bytes)', 'size', True, True, True, True, False,
                False, '', ''),
            (u'Usage Threshold', 'usage_threshold', False, True, False, True,
                False, 80, '', ''),
        ), (
            (u'Storage Block Size', 'block_size', 0, 0, 0, 'size'),
            (u'Storage Block Count', 'total_blocks', 0, 0, 0, 'size'),
            (u'Storage Used Blocks', 'used_blocks', 0, 0, 0, 'size'),
        )),
    (u'Solaris System Info',
        'host_information', 'solaris, sparc, sun, 11.2.3.10, 8072.3.2.3',
        True, True,
        u'Solaris Host', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Number of Processes', 'cpu_num', False, True, True, False, True,
                '', '', ''),
            (u'System Name', 'name', True, True, True, False, True,
                '', '', ''),
            (u'Location', 'location', True, True, True, False, True,
                '', '', ''),
            (u'Contact', 'contact', True, True, True, False, True, '', '', ''),
        ), (
            (u'CPU User Ticks', 'cpu_user_ticks', 1, 0, 86400, ''),
            (u'CPU Idle Ticks', 'cpu_idle_ticks', 1, 0, 86400, ''),
            (u'CPU Wait Ticks', 'cpu_wait_ticks', 1, 0, 86400, ''),
            (u'CPU Kernel Ticks', 'cpu_kernel_ticks', 1, 0, 86400, ''),
            (u'Swap Total', 'swap_total', 0, 0, 10000000000, ''),
            (u'Swap Available', 'swap_available', 0, 0, 10000000000, ''),
            (u'Mem Total', 'mem_total', 0, 0, 10000000000, ''),
            (u'Mem Available', 'mem_available', 0, 0, 10000000000, ''),
            (u'Load Average 1', 'load_average_1', 0, 0, 1000, ''),
            (u'Load Average 5', 'load_average_5', 0, 0, 1000, ''),
            (u'Load Average 15', 'load_average_15', 0, 0, 1000, ''),
        )),
    (u'Linux/Unix System Info',
        'host_information',
        '2021.250.10,linux,2021.250.255,freebsd,netSnmp,8072', True, True,
        u'Linux/Unix Host', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Number of Processes', 'cpu_num', False, True, True, False, True,
                '', '', ''),
            (u'CPU Usage Threshold', 'cpu_threshold', False, False, True,
                False, True,
                '80', '', ''),
            (u'System Name', 'name', True, True, True, False, True,
                '', '', ''),
            (u'Location', 'location', True, True, True, False, True,
                '', '', ''),
            (u'Contact', 'contact', True, True, True, False, True, '', '', ''),
        ), (
            (u'CPU User Ticks', 'cpu_user_ticks', 1, 0, 86400, ''),
            (u'CPU Idle Ticks', 'cpu_idle_ticks', 1, 0, 86400, ''),
            (u'CPU Nice Ticks', 'cpu_nice_ticks', 1, 0, 86400, ''),
            (u'CPU System Ticks', 'cpu_system_ticks', 1, 0, 86400, ''),
            (u'Load Average 1', 'load_average_1', 0, 0, 1000, ''),
            (u'Load Average 5', 'load_average_5', 0, 0, 1000, ''),
            (u'Load Average 15', 'load_average_15', 0, 0, 1000, ''),
            (u'Num Users', 'num_users', 0, 0, 10000, ''),
            (u'Num Procs', 'num_procs', 0, 0, 10000, ''),
            (u'TCP Active', 'tcp_active', 1, 0, 10000, ''),
            (u'TCP Passive', 'tcp_passive', 1, 0, 10000, ''),
            (u'TCP Established', 'tcp_established', 1, 0, 10000, ''),
        )),
    (u'Windows System Info',
        'host_information', 'enterprises.311', True, True,
        u'Windows Host', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Number of Processes', 'cpu_num', False, True, True, False, True,
                '1', '', ''),
            (u'CPU Usage Threshold', 'cpu_threshold', False, False, True,
                False, True,
                '80', '', ''),
            (u'System Name', 'name', True, True, True, False, True,
                '', '', ''),
            (u'Location', 'location', True, True, True, False, True,
                '', '', ''),
            (u'Contact', 'contact', True, True, True, False, True, '', '', ''),
        ), (
            (u'CPU', 'cpu', 0, 0, 100, ''),
            (u'Num Users', 'num_users', 0, 0, 10000, ''),
            (u'Num Procs', 'num_procs', 0, 0, 10000, ''),
            (u'TCP Active', 'tcp_active', 1, 0, 10000, ''),
            (u'TCP Passive', 'tcp_passive', 1, 0, 10000, ''),
            (u'TCP Established', 'tcp_established', 1, 0, 10000, ''),
        )),
    (u'Applications',
        'hostmib_apps', '', True, False,
        u'HostMIB Application', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Instances at Discovery', 'instances', True, True, True, False,
                True,
                '', '', ''),
            (u'Ignore Case', 'ignore_case', True, True, True, False, True,
                '', '', ''),
        ), (
            (u'Current Instances', 'current_instances', 0, 0, 99999, ''),
            (u'Used Memory', 'used_memory', 0, 0, 9999999, ''),
        )),
    (u'Cisco Power Supply',
        'cisco_envmib', 'PowerSupply, 5.1.2, 5.1.3', True, True,
        u'Cisco Power Supply', '', '',
        'AVERAGE', 103680, True, False, 'ent.9', (
            (u'Description', 'description', True, True, True, False, True,
                '', '', ''),
        ), (
            ()
        )),
    (u'Cisco Temperature',
        'cisco_envmib', 'Temperature, 3.1.2, 3.1.6', True, True,
        u'Cisco Temperature', '', '',
        'AVERAGE', 103680, False, False, 'ent.9', (
            (u'Description', 'description', True, True, True, False, True,
                '', '', ''),
        ), (
            (u'Temperature', 'temperature', 0, 0, 100, ''),
        )),
    (u'Cisco Voltage',
        'cisco_envmib', 'Voltage, 2.1.2, 2.1.7', True, True,
        u'Cisco Voltage', '', '',
        'AVERAGE', 103680, False, False, 'ent.9', (
            (u'Description', 'description', True, True, True, False, True,
                '', '', ''),
        ), (
            ()
        )),
    (u'Cisco SA Agent',
        'cisco_saagent', '', True, True,
        u'Cisco SA Agent', '', '',
        'AVERAGE', 103680, False, False, 'ent.9', (
            ()
        ), (
            (u'Forward Jitter', 'forward_jitter', 0, 0, 100, ''),
            (u'Backward Jitter', 'backward_jitter', 0, 0, 100, ''),
            (u'RT Latency', 'rt_latency', 0, 0, 100, ''),
            (u'Forward Packetloss', 'forward_packetloss', 0, 0, 100, ''),
            (u'Backward Packetloss', 'backward_packetloss', 0, 0, 100, ''),
        )),
    (u'Reachable',
        'reachability', '', True, True,
        u'Reachability', '', '',
        'AVERAGE', 103680, False, False, '', (
            (u'Pings to Send', 'pings', False, True, False, True, False,
                '', '', ''),
            (u'Loss Threshold%', 'threshold', False, True, False, True, False,
                '', '', ''),
            (u'Interval (ms)', 'interval', False, True, False, True, False,
                '', '', ''),
        ), (
            (u'RTT', 'rtt', 0, 0, 10000, ''),
            (u'Packetloss', 'packetloss', 0, 0, 1000, ''),
        )),
    (u'NTP',
        'ntp_client', '', False, True,
        u'NTP', '', '',
        'AVERAGE', 103680, False, False, '', (), ()),
    (u'Compaq Physical Drives',
        'cpqmib', 'phydrv', False, True,
        u'Compaq Physical Drive', '', '',
        'AVERAGE', 103680, True, False, '.', (
            (u'Controller', 'controller', True, True, False, False, True,
                '', '', ''),
            (u'Drive', 'drvindex', True, True, False, False, True,
                '', '', ''),
            (u'Drive Model', 'drive', False, True, False, False, True,
                '', '', ''),
        ), (
            ()
        )),
    (u'Compaq Fans',
        'cpqmib', 'fans', False, True,
        u'Compaq Fan', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Location', 'location', True, True, True, False, True,
                '', '', ''),
            (u'Chassis', 'chassis', False, True, True, False, True,
                '', '', ''),
            (u'Fan', 'fan_index', False, True, True, False, True,
                '', '', ''),
        ), (
            ()
        )),
    (u'Compaq Temperature',
        'cpqmib', 'temperature', False, True,
        u'Compaq Temperature', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Location', 'location', False, True, True, False, True,
                '', '', ''),
            (u'Chassis', 'chassis', False, True, True, False, True,
                '', '', ''),
            (u'Sensor', 'temp_index', False, True, True, False, True,
                '', '', ''),
        ), (
            (u'Temperature', 'temperature', 0, 0, 1000, ''),
        )),
    (u'IIS Webserver Information',
        'snmp_simple', '1.3.6.1.4.1.311.1.7.3.1.1.0|IIS Information',
        False, True,
        u'IIS Info', '', '',
        'AVERAGE', 103680, False, False, 'ent.311', (
        ), (
            (u'Total Bytes Received', 'tbr', 1, 0, 100000000, ''),
            (u'Total CGI Requests', 'tcgir', 1, 0, 100000000, ''),
            (u'Total Files Sent', 'tfs', 1, 0, 100000000, ''),
            (u'Total Gets', 'tg', 1, 0, 100000000, ''),
            (u'Total Posts', 'tp', 1, 0, 100000000, ''),
        )),
    (u'Apache',
        'apache', '', False, True,
        u'Apache', '', '',
        'AVERAGE', 103680, False, False, '', (
        ), (
            (u'Total Accesses', 'tac', 1, 0, 100000000, ''),
            (u'Total kBytes', 'tkb', 1, 0, 100000000, ''),
            (u'CPU Load', 'cplo', 0, 0, 1000, ''),
            (u'Uptime', 'up', 0, 0, 10000000, ''),
            (u'Bytes Per Request', 'bpr', 0, 0, 10000000, ''),
            (u'Busy Workers', 'bw', 0, 0, 1000, ''),
            (u'Idle Workers', 'iw', 0, 0, 1000, ''),
        )),
    (u'APC',
        'apc', '', True, True,
        u'APC', '', '',
        'AVERAGE', 103680, False, False, 'ent.318', (
            ()  # No fields
        ), (
            (u'Battery Capacity', 'capacity', 0, 0, 100, ''),
            (u'Output Load', 'load', 0, 0, 100, ''),
            (u'Input Voltage', 'in_voltage', 0, 0, 400, ''),
            (u'Output Voltage', 'out_voltage', 0, 0, 400, ''),
            (u'Time Remaining', 'time_remaining', 0, 0, 100000000, ''),
            (u'Temperature', 'temperature', 0, 0, 200, ''),
        )),
    (u'Brocade Sensors',
        'brocade_sensors', '', False, False,
        u'Brocade Sensors', '', '',
        'AVERAGE', 103680, False, False, 'ent.1588', (
            (u'Type', 'sensor_type', False, True, True, False, False,
                False, '', ''),
        ), (
            (u'Sensor Value', 'sensor_value', 0, 0, 30000000, ''),
        )),
    (u'Brocade FC Ports',
        'brocade_fcports', '', False, False,
        u'Brocade FC Ports', '', '',
        'AVERAGE', 103680, False, False, 'ent.1588', (
            (u'Physical Status', 'phy', False, True, True, False, False,
                0, '', ''),
        ), (
            (u'Tx Words', 'tx_words', 1, 0, 100000000, ''),
            (u'Rx Words', 'rx_words', 1, 0, 100000000, ''),
            (u'Tx Frames', 'tx_frames', 1, 0, 100000000, ''),
            (u'Rx Words', 'rx_frames', 1, 0, 100000000, ''),
        )),
    (u'UPS',
        'ups', '', True, True,
        u'UPS', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Identification', 'ident', False, True, True, False, True,
                '', '', ''),
            (u'UPS OID', 'ups_oid', False, True, True, False, True,
                '', '', ''),
        ), (
            (u'Battery Temperature', 'temperature', 0, 0, 200, ''),
            (u'Minutes Remaining', 'minutes_remaining', 0, 0, 10000200, ''),
            (u'Charge Remaining', 'charge_remaining', 0, 0, 10000200, ''),
        )),
    (u'UPS Input Line',
        'ups_lines', '1.3.6.1.2.1.33.1|in|0', False, True,
        u'UPS Input Line', '', '',
        'AVERAGE', 103680, False, False, '.', (
        ), (
            (u'Voltage', 'voltage', 0, 0, 500, ''),
            (u'Current', 'current', 0, 0, 500, ''),
        )),
    (u'UPS Output Line',
        'ups_lines', '1.3.6.1.2.1.33.1|out|0', False, True,
        u'UPS Output Line', '', '',
        'AVERAGE', 103680, False, False, '.', (
        ), (
            (u'Voltage', 'voltage', 0, 0, 500, ''),
            (u'Current', 'current', 0, 0, 500, ''),
            (u'Load', 'load', 0, 0, 100, ''),
        )),
    (u'Mitsubishi UPS Input Line',
        'ups_lines', '1.3.6.1.4.1.13891.101|in|1', False, True,
        u'Mitsubishi UPS Input Line', '', '',
        'AVERAGE', 103680, False, False, '.', (
        ), (
            (u'Voltage', 'voltage', 0, 0, 500, ''),
            (u'Current', 'current', 0, 0, 500, ''),
            (u'Power', 'power', 0, 0, 100000, ''),
        )),
    (u'Mitsubishi UPS Output Line',
        'ups_lines', '1.3.6.1.4.1.13891.101|out|1', False, True,
        u'Mitsubishi UPS Output Line', '', '',
        'AVERAGE', 103680, False, False, '.', (
        ), (
            (u'Voltage', 'voltage', 0, 0, 500, ''),
            (u'Current', 'current', 0, 0, 500, ''),
            (u'Power', 'power', 0, 0, 100000, ''),
            (u'Load', 'load', 0, 0, 100, ''),
        )),
    (u'Cisco PIX',
        'pix_connections', '', True, True,
        u'PIX Connection Stat', '', '',
        'AVERAGE', 103680, False,  False, 'ent.9', (
            ()  # No fields
        ), (
            (u'Connections', 'pix_connections', DS_GAUGE, 0, 1000000, ''),
        )),
    (u'Cisco NAT',
        'snmp_simple', '.1.3.6.1.4.1.9.10.77.1.2.1.0|NAT', False, True,
        u'Cisco NAT', '', '',
        'AVERAGE', 103680, False, False, 'ent.9', (
            (u'Max In Bytes', 'NatInMax', False, True, False, True, False,
                100000, "", ''),
            (u'Max Out Bytes', 'NatOutMax', False, True, False, True, False,
                100000, "", ''),
        ), (
            (u'Other IP Out', 'other_out', DS_COUNTER,
                0, 0, 'NatOutMax'),
            (u'Other IP In', 'other_in', DS_COUNTER,
                0, 0, 'NatInMax'),
            (u'ICMP Out', 'icmp_out', DS_COUNTER,
                0, 0, 'NatOutMax'),
            (u'ICMP In', 'icmp_in', DS_COUNTER,
                0, 0, 'NatInMax'),
            (u'UDP Out', 'udp_out', DS_COUNTER,
                0, 0, 'NatOutMax'),
            (u'UDP In', 'udp_in', DS_COUNTER,
                0, 0, 'NatInMax'),
            (u'TCP Out', 'tcp_out', DS_COUNTER,
                0, 0, 'NatOutMax'),
            (u'TCP In', 'tcp_in', DS_COUNTER,
                0, 0, 'NatInMax'),
            (u'Active Binds', 'active_binds', DS_GAUGE,
                0, 100000, ''),
        )),
    (u'Sensors',
        'sensors', '', True, True,
        u'Sensors', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Table Index', 'table_index', False, False, False, False, True,
                '', '', ''),
            (u'Row Index', 'row_index', False, False, False, False, True,
                '', '', ''),
            (u'Units', 'units', False, True, False, True, False, '', '', ''),
            (u'Measure', 'measure', False, True, False, True, False,
                '', '', ''),
            (u'Multiplier', 'multiplier', False, True, False, True, False,
                '', '', ''),
        ), (
            (u'Value', 'value', 0, -100000, 100000, ''),
        )),
    (u'OS/400 System Info',
        'snmp_simple', '.1.3.6.1.4.1.2.6.4.5.1.0|OS400', True, True,
        u'OS/400 Host', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'CPU Threshold', 'cpu_threshold', False, True, False, True,
                False, 90, '', ''),
        ), (
            (u'CPU Usage', 'cpu400', DS_GAUGE, 0, 100000, ''),
        )),
    (u'Dell Chassis',
        'snmp_simple', '.1.3.6.1.4.1.674.10892.1.200.10.1.2.1|Chassis status',
        True, True,
        u'Dell Chassis', '', '',
        'AVERAGE', 103680, False, False, '.', (
            ()  # No fields
        ), (
            (u'Fan #1 RPM', 'fan1', DS_GAUGE, 0, 100000, ''),
            (u'Fan #2 RPM', 'fan2', DS_GAUGE, 0, 100000, ''),
            (u'Fan #3 RPM', 'fan3', DS_GAUGE, 0, 100000, ''),
            (u'Fan #4 RPM', 'fan4', DS_GAUGE, 0, 100000, ''),
            (u'Fan #5 RPM', 'fan5', DS_GAUGE, 0, 100000, ''),
            (u'Fan #6 RPM', 'fan6', DS_GAUGE, 0, 100000, ''),
            (u'Fan #7 RPM', 'fan7', DS_GAUGE, 0, 100000, ''),
        )),
    (u'Generic FC Ports',
        'fc_ports', '', True, False,
        u'Fibre Channel Interface', '', '',
        'AVERAGE', 103680, False, False, '.',
        (), ()),  # FIXME
    (u'Cisco 802.11X Device',
        'snmp_simple', '.1.3.6.1.4.1.9.9.273.1.1.2.1.1.1|Cisco AP',
        False, True,
        u'Cisco 802.11X Device', '', '',
        'AVERAGE', 103680, False, False, 'ent.9', (
        ), (
            (u'Associated', 'associated', 0, 0, 2100, ''),
        )),
    (u'Compaq Power Supply',
        'cpqmib', 'powersupply', False, True,
        u'Compaq Power Supply', '', '',
        'AVERAGE', 103680, False, False, '.', (
            (u'Chassis', 'chassis', False, False, False, False, True,
                '', '', ''),
            (u'Bay Index', 'bayindex', False, False, False, False, True,
                '', '', ''),
        ), (
            ()  # No RRDs
        )),
    )
