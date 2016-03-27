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
""" Graph related database fields
 See widges.graph.py for details"""
graph_types = (
    #Cisco MAC Accounting | Accounted Bytes | cisco_mac_bytes
    #Cisco MAC Accounting | Accounted Packets | cisco_mac_packets

    (u'Apache', (
        (u'CPU Load', u'', 'area', '', (
            ('cplo', '', 'CPU Load', '%.3lf'),
        )),
        (u'Hits', u'Hits', 'area', '', (
            ('tac', '', 'Hits per Second', '%6.2f %sHits/s'),
        )),
        (u'Throughput', u'Bps', 'area',  '', (
            ('tkb', '1000,*', 'Throughput', '%6.2f %sB/s'),
        )),
        (u'Request Size', u'B/Req', 'area',  '', (
            ('bpr', '', 'Bytes/Request', '%6.2f %sB'),
        )),
        (u'Workers', 'Workers', 'ufarea',  '', (
            ('bw', '', 'Busy Workers', '%6d'),
            ('iw', '', 'Idle Workers', '%6d'),
        )),
    )),
    (u'APC', (
        (u'Battery Temperature', 'Deg', 'area', '', (
            ('temperature', '', 'Temperature', '%4.0f'),
        )),
        (u'Load/Capacity', '%', 'area', '', (
            ('capacity', '', 'Battery Capacity', '%6.2f %%'),
            ('load', '', 'Output Load', '%6.2f %%'),
        )),
        (u'Voltages', 'V', 'lines', '', (
            ('in_voltage', '', 'Input Voltage',  '%5.0f VAC'),
            ('out_voltage', '', 'Output Voltage',  '%5.0f VAC'),
        )),
        (u'Time Remaining', 'Minutes', 'area', '', (
            ('time_remaining', '', 'Time Remaining', '%5.0f mins'),
        )),
    )),
    (u'Applications', (
        (u'Threads', 'Threads', 'area', '', (
            ('current_instances', '', 'Threads', '%5.0f'),
        )),
        (u'Memory', 'Bytes', 'area', '', (
            ('used_memory', '', 'Memory', '%6.2f %sB'),
        )),
    )),
    (u'BGP Neighbors', (
        (u'Updates', 'Updates', 'inout', '', (
            ('bgpin', '300,*', 'Inbound Updates in 5 mins', '%4.0f %s'),
            ('bgpout', '300,*', 'Outbound Updates in 5 mins', '%4.0f %s'),
        )),
        (u'Routes', 'Routes', 'inout', '', (
            ('accepted_routes', '', 'Accepted Routes', '%6.2f %s'),
            ('advertised_routes', '', 'Advertised Routes', '%6.2f %s'),
        )),
    )),
    (u'Brocade FC Ports', (
        (u'Traffic', 'bps', 'inout', '', (
            ('rx_words', '32,*', 'Inbound', '%6.2f %sbps'),
            ('tx_words', '32,*', 'Outbound', '%6.2f %sbps'),
        )),
        (u'Frames', 'Fps', 'inout', '', (
            ('rx_frames', '', 'Inbound', '%6.2f %sFps'),
            ('tx_frames', '', 'Outbound', '%6.2f %sFps'),
        )),
    )),
    (u'Brocade Sensors', (
        (u'Sensor Value', '$unit', 'area', '', (
            ('sensor_value', '', '$measure', '%5.0f'),
        )),
    )),
    (u'Cisco 802.11X Device', (
        (u'Associated Devices', 'Clients', 'area', '', (
            ('associated', '', 'Associated Clients', '%3.0f'),
        )),
    )),
    (u'Cisco System Info', (
        (u'CPU Load', '%', 'area', '', (
            ('cpu', '', 'CPU Utilization', '%4.0f %%'),
        )),
        (u'Memory', '%', 'ufarea', '', (
            ('mem_used', '', 'Used Memory', '%6.2f %sB'),
            ('mem_free', '', 'Free Memory', '%6.2f %sB'),
        )),
    )),
    (u'Cisco Temperature', (
        (u'Temperature', 'deg', 'area', '', (
            ('temperature', '', 'Temperature', '%5.0f'),
        )),
    )),
    (u'Cisco SA Agent', (
        (u'Round Trip Latency', 'msec', 'area', '', (
            ('rt_latency', '', 'Round-Trip Latency', '%5.0f msec'),
        )),
        (u'Jitter', '', 'inout', '', (
            ('forward_jitter', '', 'Forward Jitter', '%5.0f'),
            ('backward_jitter', '', 'Backward Jitter', '%5.0f'),
        )),
        (u'Packet Loss', '', 'inout', '', (
            ('forward_packetloss', '', 'Forward Packetloss', '%5.0f'),
            ('backward_packetloss', '', 'Backward Packetloss', '%5.0f'),
        )),
    )),

    (u'Linux/Unix System Info', (
        (u'CPU Usage', '%', 'pctarea', 'rigid upper-limit=100', (
            ('cpu_user_ticks', '$cpu_num,/', 'User Time', '%6.2f %%'),
            ('cpu_nice_ticks', '$cpu_num,/', 'Nice Time', '%6.2f %%'),
            ('cpu_system_ticks', '$cpu_num,/', 'System Time', '%6.2f %%'),
            ('cpu_idle_ticks', '$cpu_num,/', 'Idle Time', '%6.2f %%'),
        )),
        (u'Load Average', 'Load', 'lines', '', (
            ('load_average_1', '', ' 1 Minute  Load Average', '%5.2lf'),
            ('load_average_5', '', ' 5 Minutes Load Average', '%5.2lf'),
            ('load_average_15', '', '15 Minutes Load Average', '%5.2lf'),
        )),
        (u'Processes', 'procs', 'area', '', (
            ('num_procs', '', 'Processes', '%8.0lf'),
        )),
        (u'Users', 'Users', 'area', '', (
            ('num_users', '', 'Users', '%8.0lf'),
        )),
        (u'TCP Connection Status', 'Connections', 'lines', '', (
            ('tcp_established', '300,*', 'Established Connections', '%8.0lf'),
            ('tcp_active', '300,*', 'Outgoing Connections', '%8.0lf'),
            ('tcp_passive', '300,*', 'Incoming Connections', '%8.0lf'),
        )),
    )),
    (u'Mitsubishi UPS Input Line', (
        (u'Voltage', 'V', 'area', '', (
            ('voltage', '', 'Voltage', '%3.0f'),
        )),
        (u'Current', 'Amps', 'area', '', (
            ('current', '', 'Current', '%6.2f %sAmp'),
        )),
    )),
    (u'Mitsubishi UPS Output Line', (
        (u'Voltage', 'V', 'area', '', (
            ('voltage', '', 'Voltage', '%3.0f'),
        )),
        (u'Current', 'Amps', 'area', '', (
            ('current', '', 'Current', '%6.2f %sAmp'),
        )),
    )),
    (u'Physical Interfaces', (
        (u'Traffic', u'bps', 'inout', '', (
            ('input', '8,*', 'Inbound', '%6.2f %sbps'),
            ('output', '8,*', 'Outbound', '%6.2f %sbps'),
        )),
        (u'Packets', u'Pps', 'inout', '', (
            ('inpackets', '', 'Inbound', '%6.2f %spps'),
            ('outpackets', '', 'Outbound', '%6.2f %spps'),
        )),
        (u'Errors', u'Eps', 'inout', '', (
            ('inputerrors', '', 'Input Errors', '%6.2f %sEps'),
            ('outputerrors', '', 'Output Errors', '%6.2f %sEps'),
        )),
    )),
    (u'Reachable', (
        (u'Packet Loss', '%', 'area', '', (
            ('packetloss', '', 'Packet Loss', '%5.0f %%'),
        )),
        (u'Round Trip Time', 'msec', 'area', '', (
            ('rtt', '', 'Round Trip Time', '%5.0f ms'),
        )),
    )),
    (u'Sensors', (
        (u'Sensor Value', '$unit', 'area', '', (
            ('value', '${multiplier},*', '$measure', '%6.2f %s${units}'),
        )),
    )),
    (u'Storage', (
        (u'Used Storage', 'Bytes', 'mtuarea', '', (
            ('block_size', '', 'Free Storage', '%6.2f %sB'),
            ('total_blocks', '', 'Total Storage', '%6.2f %sB'),
            ('used_blocks', '', 'Used Storage', '%6.2f %sB'),
        )),
    )),
    (u'TCP Ports', (
        (u'Established Connections',  'Connections', 'lines', '', (
            ('tcp_established', '', 'Established Connections', '%8.0lf'),
        )),
        (u'Connection Delay', 'Seconds', 'lines', '', (
            ('conn_delay', '', 'Connection Delay', '%6.2f %ssec'),
        )),
    )),
    (u'UPS', (
        (u'Batttery Temperature', 'Deg', 'area', '', (
            ('temperature', '', 'Temperature', '%5.0f'),
        )),
        (u'Time Remaining', 'Minutes', 'area', '', (
            ('minutes_remaining', '', 'Time Remaining', '%3.0f'),
        )),
        (u'Charge Remaining', '%', 'area', '', (
            ('charge_remaining', '', 'Charge Remaining', '%3.0f %%'),
        )),
    )),
    (u'UPS Input Line', (
        (u'Voltage', 'V', 'area', '', (
            ('voltage', '', 'Voltage', '%3.0f'),
        )),
        (u'Current', 'Amps', 'area', '', (
            ('current', '', 'Current', '%6.2f %sAmp'),
        )),
    )),
    (u'UPS Output Line', (
        (u'Voltage', 'V', 'area', '', (
            ('voltage', '', 'Voltage', '%4.0f V'),
        )),
        (u'Current', 'Amps', 'area', '', (
            ('current', '', 'Current', '%6.2f %sAmp'),
        )),
    )),
    (u'Windows System Info', (
        (u'CPU Load', '%', 'area', '', (
            ('cpu', '', 'CPU Utilization', '%6.2f %%'),
        )),
        (u'Processes', 'procs', 'area', '', (
            ('num_procs', '', 'Processes', '%6f'),
        )),
        (u'Users', 'Users', 'area', '', (
            ('num_users', '', 'Users', '%6.0f'),
        )),
        (u'TCP Connection Status', 'Connections', 'lines', '', (
            ('tcp_established', '300,*', 'Established Connections', '%6.0f'),
            ('tcp_active', '300,*', 'Outgoing Connections', '%6.0f'),
            ('tcp_passive', '300,*', 'Incoming Connections', '%6.0f'),
        )),
    )),

)
