# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011-2013 Craig Small <csmall@enc.com.au>
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

alarm_states = [
    [u'down', 10, 'down.wav', 'up.wav', 1],
    [u'up', 100, '', '', 2], 
    [u'alert', 60, 'boing.wav', '', 3], 
    [u'testing', 40, '', '', 4], 
    [u'running', 100, '', '', 2], 
    [u'not running', 20, '', '', 1], 
    [u'open', 100, '', '', 2], 
    [u'closed', 15, '', '', 1], 
    [u'error', 90, 'boing.wav', '', 3], 
    [u'invalid', 30, '', '', 1], 
    [u'valid', 110, '', '', 2], 
    [u'reachable', 100, '', '', 2], 
    [u'unreachable', 5, '', '', 1], 
    [u'lowerlayerdown', 10, 'down.wav', 'up.wav', 1], 
    [u'synchronized', 100, '', '', 2], 
    [u'unsynchronized', 6, '', '', 1], 
    [u'battery normal', 100, '', '', 2], 
    [u'battery low', 4, '', '', 1], 
    [u'battery unknown', 2, '', '', 1], 
    [u'on battery', 3, '', '', 1], 
    [u'on line', 90, '', '', 2], 
    [u'ok', 100, '', '', 2], 
    [u'out of bounds', 10, '', '', 1], 
    [u'unavailable', 10, 'down.wav', 'up.wav', 1], 
    [u'available', 100, '', '', 2], 
    [u'battery depleted', 3, '', '', 1], 
    [u'other', 10, '', '', 1], 
    [u'unknown', 10, '', '', 1], 
    [u'noncritical', 90, '', '', 1], 
    [u'critical', 10, '', '', 1], 
    [u'nonrecoverabl', 10, '', '', 1], 
    [u'warning', 80, 'down.wav', 'up.wav', 1]
    ]

autodiscovery_policies = [
    [u'No Autodiscovery',1,0,0,0,0,0,1,1,1],
    [u'Standard'        ,1,1,0,1,0,1,1,1,1],
    [u'Automagic'       ,1,1,1,1,1,0,1,1,1],
    [u'Administrative'  ,0,1,1,1,0,1,1,1,1],
    [u'Just Inform'     ,0,0,0,1,0,0,0,1,1],
    [u'Standard (for Switches)',1,1,0,1,1,0,1,1,0]
    ]
#showable 2=1,0 1=1,1 0=0,0
#RRD Types = 1:gauge, 2:counter, 3:absolute
attribute_types = [
        ['No Interface Type',0,0,'none','',u'No Poller','AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['TCP Ports',0,1,'tcp_ports','500,600-1024',u'TCP/IP Port','LAST','103680',1,23,0,'tcp_ports',1,1,1,'',[
            ['Port Number','port',0,1,1,1,0,0,'',''],
            ['Check Content','check_content',0,1,0,1,0,0,'',''],
            ['Check Content URL','check_url',0,1,1,0,1,0,'',''],
            ['Check Content RegExp','check_regexp',0,1,0,1,0,0,'','']
            ], [
            [u'Established Connections', 'tcp_established', 0,0,10000,0],
            [u'Connection Delay', 'conn_delay', 0,0,10000,0],
            ] ],
        ['Cisco System Info',1,1,'host_information','cisco,9.1,9.5',u'Cisco Router','AVERAGE','103680',300,9,0,'none',0,7,0,'ent.9',[
            ['Number of Processors','cpu_num',0,1,1,1,0,1,'',''],
            ['CPU Usage Threshold','cpu_threshold',0,1,0,1,0,60,'',''],
            ['System Name','name',1,1,1,1,0,1,'',''],
            ['Location','location',1,1,1,1,0,1,'',''],
            ['Contact','contact',1,1,1,1,0,1,'',''],
           ], [
            [u'CPU', 'cpu', 0,0,100,''],
            [u'Mem Used', 'mem_used', 0,0,100000000000,''],
            [u'Mem Free', 'mem_free', 0,0,100000000000,''],
            [u'Acct Packets', 'acct_packets', 2,0,100000000000,''],
            [u'Acct Bytes', 'acct_bytes', 0,0,100000000000,''],
            [u'TCP Active', 'tcp_active', 1,0,10000000,''],
            [u'TCP Passive', 'tcp_passive', 1,0,10000000,''],
            [u'TCP Established', 'tcp_established', 1,0,10000000,''],
               ] ],
        ['Physical Interfaces',1,1,'snmp_interfaces','',u'SNMP Interface','AVERAGE','103680',300,3,1,'none',0,1,1,'.',[
            ['IP Address','address',1,1,1,1,0,'','',''],
            ['IP Mask','mask',0,1,1,1,0,'','',''],
            ['Peer Address','peer',0,1,1,1,0,'','',''],
            ['Speed','speed',0,1,1,1,0,1,'',''],
            ['Percentile','percentile',0,1,0,1,0,'','',''],
            ['Flip In Out in Graphs','flipinout',0,1,1,1,0,0,'',''],
            ['Pings to Send','pings',0,1,1,1,0,50,'',''],
            ['Fixed Admin Status','fixed_admin_status',0,1,1,1,0,0,'','']
            ], [
            [u'Input Bytes', 'input', 1,0,0,'speed'],
            [u'Output Bytes', 'output', 1,0,0,'speed'],
            [u'Input Errors', 'inputerrors', 1,0,0,'speed'],
            [u'Output Errors', 'outputerrors', 1,0,0,'speed'],
            [u'Round Trip Time', 'rtt', 0,0,10000,''],
            [u'Packet Loss', 'packetloss', 0,0,1000,''],
            [u'Input Packets', 'inpackets', 1,0,0,'speed'],
            [u'Output Packets', 'outpackets', 1,0,0,'speed'],
            [u'Drops', 'drops', 1,0,0,'speed'],
                ] ],

        ['BGP Neighbors',1,1,'bgp_peers','',u'BGP Neighbor','AVERAGE','103680',300,90,0,'none',0,1,0,'.',[
            ['Local IP','local',1,1,1,0,1,'','',''],
            ['Remote IP','remote',0,1,1,0,0,'','',''],
            ['Autonomous System','asn',1,1,1,0,1,'','',''],
            ], [
            [u'BGP In Updates', 'bgpin', 1,0,10000000,''],
            [u'BGP Out Updates', 'bgpout', 1,0,10000000,''],
            [u'BGP Uptime', 'bgpuptime', 0,0,10000000,''],
            [u'Accepted Routes', 'accepted_routes', 0,0,9000000,''],
            [u'Advertised Routes', 'advertised_routes', 0,0,9000000,''],
                ] ],
        ['Storage',1,1,'storage','',u'Storage Device','AVERAGE','103680',300,15,0,'none',0,9,0,'.',[
            ['Disk Type','storage_type',1,1,1,0,0,'','',''],
            ['Size (bytes)','size',1,1,1,1,0,'','',''],
            ['Usage Threshold','usage_threshold',0,1,0,1,0,80,'',''],
            ], [
            [u'Storage Block Size', 'storage_block_size', 0,0,0,'size'],
            [u'Storage Block Count', 'storage_block_count', 0,0,0,'size'],
            [u'Storage Used Blocks', 'storage_used_blocks', 0,0,0,'size'],
                ] ],
        ['Solaris System Info',1,1,'host_information','solaris,sparc,sun,11.2.3.10,8072.3.2.3',u'Solaris Host','AVERAGE','103680',300,20,0,'none',0,1,0,'.',[
            [u'Number of Processes','cpu_num',0,1,1,0,1,'1','',''],
            [u'System Name','name',1,1,1,0,1,'','',''],
            [u'Location','location',1,1,1,0,1,'','',''],
            [u'Contact','contact',1,1,1,0,1,'','',''],
            ], [
            [u'CPU User Ticks', 'cpu_user_ticks', 1,0,86400,''],
            [u'CPU Idle Ticks', 'cpu_idle_ticks', 1,0,86400,''],
            [u'CPU Wait Ticks', 'cpu_wait_ticks', 1,0,86400,''],
            [u'CPU Kernel Ticks', 'cpu_kernel_ticks', 1,0,86400,''],
            [u'Swap Total', 'swap_total', 0,0,10000000000,''],
            [u'Swap Available', 'swap_available', 0,0,10000000000,''],
            [u'Mem Total', 'mem_total', 0,0,10000000000,''],
            [u'Mem Available', 'mem_available', 0,0,10000000000,''],
            [u'Load Average 1', 'load_average_1', 0,0,1000,''],
            [u'Load Average 5', 'load_average_5', 0,0,1000,''],
            [u'Load Average 15', 'load_average_15', 0,0,1000,''],
                ] ],
        ['Linux/Unix System Info',1,1,'host_information','2021.250.10,linux,2021.250.255,freebsd,netSnmp,8072',u'Linux/Unix Host','AVERAGE','103680',300,21,0,'none',0,10,0,'.',[
            [u'Number of Processes','cpu_num',0,1,1,0,1,'1','',''],
            [u'CPU Usage Threshold','cpu_threshold',0,0,1,0,1,'80','',''],
            [u'System Name','name',1,1,1,0,1,'','',''],
            [u'Location','location',1,1,1,0,1,'','',''],
            [u'Contact','contact',1,1,1,0,1,'','',''],
            ], [
            [u'CPU User Ticks', 'cpu_user_ticks', 1,0,86400,''],
            [u'CPU Idle Ticks', 'cpu_idle_ticks', 1,0,86400,''],
            [u'CPU Nice Ticks', 'cpu_nice_ticks', 1,0,86400,''],
            [u'CPU System Ticks', 'cpu_system_ticks', 1,0,86400,''],
            [u'Load Average 1', 'load_average_1', 0,0,1000,''],
            [u'Load Average 5', 'load_average_5', 0,0,1000,''],
            [u'Load Average 15', 'load_average_15', 0,0,1000,''],
            [u'Num Users', 'num_users', 0,0,10000,''],
            [u'Num Procs', 'num_procs', 0,0,10000,''],
            [u'TCP Active', 'tcp_active', 1,0,10000,''],
            [u'TCP Passive', 'tcp_passive', 1,0,10000,''],
            [u'TCP Established', 'tcp_established', 1,0,10000,''],
                ] ],
        ['Windows System Info',1,1,'host_information','enterprises.311',u'Windows Host','AVERAGE','103680',300,28,0,'none',0,11,0,'.',[
            [u'Number of Processes','cpu_num',0,1,1,0,1,'1','',''],
            [u'CPU Usage Threshold','cpu_threshold',0,0,1,0,1,'80','',''],
            [u'System Name','name',1,1,1,0,1,'','',''],
            [u'Location','location',1,1,1,0,1,'','',''],
            [u'Contact','contact',1,1,1,0,1,'','',''],
            ], [
            [u'CPU', 'cpu', 0,0,100,''],
            [u'Num Users', 'num_users', 0,0,10000,''],
            [u'Num Procs', 'num_procs', 0,0,10000,''],
            [u'TCP Active', 'tcp_active', 1,0,10000,''],
            [u'TCP Passive', 'tcp_passive', 1,0,10000,''],
            [u'TCP Established', 'tcp_established', 1,0,10000,''],
                ] ],
        ['Applications',1,0,'hostmib_apps','',u'HostMIB Application','AVERAGE','103680',300,44,0,'none',0,1,0,'.',[
            [u'Instances at Discovery','instances',1,1,1,0,1,'','',''],
            [u'Ignore Case','ignore_case',1,1,1,0,1,'','',''],
            ], [
            [u'Current Instances', 'current_instances', 0,0,99999,''],
            [u'Used Memory', 'used_memory', 0,0,9999999,''],
                ] ],
        ['Cisco Power Supply',1,1,'cisco_envmib','PowerSupply,5.1.2,5.1.3',u'Cisco Power Supply','','103680',300,1,1,'none',0,1,0,'ent.9',[
            ], [
                ] ],
        ['Cisco Temperature',1,1,'cisco_envmib','Temperature,3.1.2,3.1.6',u'Cisco Temperature','AVERAGE','103680',300,37,1,'none',0,1,0,'ent.9',[
            ], [
            [u'Temperature', 'temperature', 0,0,100,''],
                ] ],
        ['Cisco Voltage',1,1,'cisco_envmib','Voltage,2.1.2,2.1.7',u'Cisco Voltage','AVERAGE','103680',300,1,1,'none',0,1,0,'ent.9',[ ], [ ] ],
        ['Cisco SA Agent',1,1,'cisco_saagent','',u'Cisco SA Agent','AVERAGE','103680',300,39,0,'none',0,1,0,'ent.9',[
            ], [
            [u'Forward Jitter', 'forward_jitter', 0,0,100,''],
            [u'Backward Jitter', 'backward_jitter', 0,0,100,''],
            [u'RT Latency', 'rt_latency', 0,0,100,''],
            [u'Forward Packetloss', 'forward_packetloss', 0,0,100,''],
            [u'Backward Packetloss', 'backward_packetloss', 0,0,100,''],
                ] ],
        ['Reachable',1,1,'reachability','',u'Reachability','AVERAGE','103680',300,41,0,'none',0,1,0,'',[
            [u'Pings to Send','pings',0,1,0,1,0,'','',''],
            [u'Loss Threshold%','threshold',0,1,0,1,0,'','',''],
            [u'Interval (ms)','interval',0,1,0,1,0,'','',''],
            ], [
            [u'RTT', 'rtt', 0,0,10000,''],
            [u'Packetloss', 'packetloss', 0,0,1000,''],
                ] ],
        ['NTP',0,1,'ntp_client','',u'NTP','AVERAGE','103680',300,1,0,'none',0,1,0,'',[], [] ],
        ['UDP Ports',0,0,'tcp_ports','-sU -p1-500,600-1024 --host_timeout 15000',u'UDP/IP Port','AVERAGE','103680',300,45,0,'tcp_ports',1,1,0,'',[
            ], [
            [u'Connection Delay', 'conn_delay', 0,0,10000,''],
                ] ],
        ['Compaq Physical Drives',0,1,'cpqmib','phydrv',u'Compaq Physical Drive','AVERAGE','103680',300,1,0,'none',0,1,0,'.',[
            [u'Controller', 'controller', 1,1,0, 0,1, '','',''],
            [u'Drive', 'drvindex', 1,1,0, 0,1, '','',''],
            [u'Drive Model', 'drive', 0,1,0, 0,1, '','',''],
            ], [
                ] ],
        ['Compaq Fans',0,1,'cpqmib','fans',u'Compaq Fan','AVERAGE','103680',300,1,0,'none',0,1,0,'.',[
            [u'Location', 'location', 1,1,1, 0,1, '','',''],
            [u'Chassis', 'chassis', 0,1,1, 0,1, '','',''],
            [u'Fan', 'fan_index', 0,1,1, 0,1, '','',''],
            ], [
                ] ],
        ['Compaq Temperature',0,1,'cpqmib','temperature',u'Compaq Temperature','AVERAGE','103680',300,46,0,'none',0,1,0,'.',[
            [u'Location', 'location', 0,1,1, 0,1, '','',''],
            [u'Chassis', 'chassis', 0,1,1, 0,1, '','',''],
            [u'Sensor', 'temp_index', 0,1,1, 0,1, '','',''],
            ], [
            [u'Temperature', 'temperature', 0,0,1000,''],
                ] ],
        ['IIS Webserver Information',0,1,'snmp_simple','1.3.6.1.4.1.311.1.7.3.1.1.0|IIS Information',u'IIS Info','AVERAGE','103680',300,50,0,'none',0,1,0,'ent.311',[
            ], [
            [u'Total Bytes Received', 'tbr', 1,0,100000000,''],
            [u'Total CGI Requests', 'tcgir', 1,0,100000000,''],
            [u'Total Files Sent', 'tfs', 1,0,100000000,''],
            [u'Total Gets', 'tg', 1,0,100000000,''],
            [u'Total Posts', 'tp', 1,0,100000000,''],
                ] ],
        ['Apache',0,1,'apache','',u'Apache','AVERAGE','103680',300,53,0,'none',1,1,0,'',[
            ], [
            [u'Total Accesses', 'tac', 1,0,100000000,''],
            [u'Total kBytes', 'tkb', 1,0,100000000,''],
            [u'CPU Load', 'cplo', 0,0,1000,''],
            [u'Uptime', 'up', 0,0,10000000,''],
            [u'Bytes Per Request', 'bpr', 0,0,10000000,''],
            [u'Busy Workers', 'bw', 0,0,1000,''],
            [u'Idle Workers', 'iw', 0,0,1000,''],
                ] ],
        ['APC',1,1,'apc','',u'APC','AVERAGE','103680',300,61,0,'none',0,1,0,'ent.318',[
            ], [
            [u'Battery Capacity', 'capacity', 0,0,100,''],
            [u'Output Load', 'load', 0,0,100,''],
            [u'Input Voltage', 'in_voltage', 0,0,400,''],
            [u'Output Voltage', 'out_voltage', 0,0,400,''],
            [u'Time Remaining', 'time_remaining', 0,0,100000000,''],
            [u'Temperature', 'temperature', 0,0,200,''],
                ] ],
        ['Alteon Real Server',1,1,'alteon_realservers','',u'Alteon Real Server','AVERAGE','103680',300,66,0,'none',0,1,0,'ent.1872',[
            [u'Hostname', 'hostname', 1,1,1, 1,0, '','',''],
            [u'Max Connections', 'max_connections', 0,1,1, 1,0, '','',''],
            ], [
            [u'Total Sessions', 'total_sessions', 1,0,100000000,''],
            [u'Current Sessions', 'current_sessions', 0,0,0,'max_connections'],
            [u'Failures', 'failures', 1,0,10000,''],
            [u'Octets', 'octets', 1,0,100000000,''],
                ] ],
        ['Alteon Virtual Server',0,1,'alteon_virtualservers','',u'Alteon Virtual Server','AVERAGE','103680',300,70,0,'none',0,1,0,'ent.1872',[
            [u'Hostname', 'hostname', 1,1,1, 1,0, '','',''],
            ], [
            [u'Total Sessions', 'total_sessions', 1,0,100000000,''],
            [u'Current Sessions', 'current_sessions', 0,0,20000,''],
            [u'Octets', 'octets', 1,0,100000000,''],
                ] ],
        ['Alteon Real Services',0,1,'alteon_realservices','',u'Alteon Real Services','AVERAGE','103680',300,73,0,'none',0,1,0,'ent.1872',[
            [u'Hostname', 'hostname', 1,1,1, 1,0, '','',''],
            [u'Address', 'address', 1,1,1, 1,0, '','',''],
            [u'Port', 'port', 1,1,1, 1,0, '','',''],
            [u'Real Server', 'real_server', 0,0,1, 0,1, '','',''],
            ], [
            [u'Response Time', 'response_time', 0,0,10000,''],
                ] ],
        ['Alteon System Info',1,1,'host_information','enterprises.1872',u'Alteon System Info','AVERAGE','103680',300,75,0,'none',0,1,0,'ent.1872',[
            [u'System Name','name',1,1,1,0,1,'','',''],
            [u'Location','location',1,1,1,0,1,'','',''],
            [u'Contact','contact',1,1,1,0,1,'','',''],
            [u'Number of CPUs','cpu_num',0,0,1, 0,0, '','',''],
            ], [
            [u'TCP Active', 'tcp_active', 1,0,10000,''],
            [u'TCP Passive', 'tcp_passive', 1,0,10000,''],
            [u'TCP Established', 'tcp_established', 1,0,10000,''],
            [u'Memory Total', 'mem_total', 0,0,10000000000,''],
            [u'Memory Used', 'mem_used', 0,0,10000000000,''],
            [u'CPU A 1 sec', 'cpua_1sec', 0,0,1000,''],
            [u'CPU A 4 sec', 'cpua_4sec', 0,0,1000,''],
            [u'CPU A 64 sec', 'cpua_64sec', 0,0,1000,''],
            [u'CPU B 1 sec', 'cpub_1sec', 0,0,1000,''],
            [u'CPU B 4 sec', 'cpub_4sec', 0,0,1000,''],
            [u'CPU B 64 sec', 'cpub_64sec', 0,0,1000,''],
                ] ],
        ['Brocade Sensors',0,0,'brocade_sensors','',u'Brocade Sensors','AVERAGE','103680',300,77,0,'none',0,1,0,'ent.1588',[
            [u'Type','sensor_type',0,1,1, 0,0,'','',''],
            ], [
            [u'Sensor Value', 'sensor_value', 0,0,30000000,''],
                ] ],
        ['Brocade FC Ports',0,0,'brocade_fcports','',u'Brocade FC Ports','AVERAGE','103680',300,78,0,'none',0,1,0,'ent.1588',[
            [u'Physical Status','phy',0,1,1, 0,0,'','',''],
            ], [
            [u'Tx Words', 'tx_words', 1,0,100000000,''],
            [u'Rx Words', 'rx_words', 1,0,100000000,''],
            [u'Tx Frames', 'rx_frames', 1,0,100000000,''],
            [u'Rx Words', 'rx_frames', 1,0,100000000,''],
                ] ],
        ['UPS',1,1,'ups','',u'UPS','AVERAGE','103680',300,84,0,'none',0,1,0,'.',[
            [u'Identification','ident',0,1,1, 0,1,'','',''],
            [u'UPS OID','ups_oid',0,1,1, 0,1,'','',''],
            ], [
            [u'Battery Temperature', 'temperature', 0,0,200,''],
            [u'Minutes Remaining', 'minutes_remaining', 0,0,10000200,''],
            [u'Charge Remaining', 'charge_remaining', 0,0,10000200,''],
                ] ],
        ['UPS Input Line',0,1,'ups_lines','1.3.6.1.2.1.33.1|in|0',u'UPS Input Line','AVERAGE','103680',300,85,0,'none',0,1,0,'.',[
            ], [
            [u'Voltage', 'voltage', 0,0,500,''],
            [u'Current', 'current', 0,0,500,''],
                ] ],
        ['UPS Output Line',0,1,'ups_lines','1.3.6.1.2.1.33.1|out|0',u'UPS Output Line','AVERAGE','103680',300,85,0,'none',0,1,0,'.',[
            ], [
            [u'Voltage', 'voltage', 0,0,500,''],
            [u'Current', 'current', 0,0,500,''],
            [u'Load', 'load', 0,0,100,''],
                ] ],
        ['Mitsubishi UPS Input Line',0,1,'ups_lines','1.3.6.1.4.1.13891.101|in|1',u'Mitsubishi UPS Input Line','AVERAGE','103680',300,85,0,'none',0,1,0,'.',[
            ], [
            [u'Voltage', 'voltage', 0,0,500,''],
            [u'Current', 'current', 0,0,500,''],
            [u'Power', 'power', 0,0,100000,''],
                ] ],
        ['Mitsubishi UPS Output Line',0,1,'ups_lines','1.3.6.1.4.1.13891.101|out|1',u'Mitsubishi UPS Output Line','AVERAGE','103680',300,85,0,'none',0,1,0,'.',[
            ], [
            [u'Voltage', 'voltage', 0,0,500,''],
            [u'Current', 'current', 0,0,500,''],
            [u'Power', 'power', 0,0,100000,''],
            [u'Load', 'load', 0,0,100,''],
                ] ],
        ['Cisco PIX',1,1,'pix_connections','',u'PIX Connection Stat','AVERAGE','103680',300,91,0,'none',0,1,0,'ent.9',[], [] ],
        ['Cisco NAT',0,1,'snmp_simple','.1.3.6.1.4.1.9.10.77.1.2.1.0|NAT',u'Cisco NAT','AVERAGE','103680',300,93,0,'none',0,1,0,'ent.9',[], [] ],
        ['Sensors',1,1,'sensors','',u'Sensors','AVERAGE','103680',300,94,1,'none',0,1,0,'.',[
            [u'Table Index','table_index',0,0,0, 0,1,'','',''],
            [u'Row Index','row_index',0,0,0, 0,1,'','',''],
            [u'Units','units',0,1,0, 1,0,'','',''],
            [u'Measure','measure',0,1,0, 1,0,'','',''],
            [u'Multiplier','multiplier',0,1,0, 1,0,'','',''],
            ], [
            [u'Value', 'value', 0,-100000,100000,''],
                ] ],
        ['OS/400 System Info',1,1,'snmp_simple','.1.3.6.1.4.1.2.6.4.5.1.0|OS400',u'OS/400 Host','AVERAGE','103680',300,95,0,'none',0,1,0,'.',[], [] ],
        ['Dell Chassis',1,1,'snmp_simple','.1.3.6.1.4.1.674.10892.1.200.10.1.2.1|Chassis status',u'Dell Chassis','AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['Generic FC Ports',1,0,'fc_ports','',u'Fibre Channel Interface','AVERAGE','103680',300,105,0,'none',0,1,0,'.',[], [] ],
        ['Cisco 802.11X Device',1,0,'snmp_simple','.1.3.6.1.4.1.9.9.273.1.1.2.1.1.1|Cisco AP',u'Cisco 802.11X Device','AVERAGE','103680',300,101,0,'none',0,1,0,'ent.9',[
            ], [
            [u'Associated', 'associated', 0,0,2100,''],
                ]],
        ['Compaq Power Supply',1,0,'cpqmib','powersupply',u'Compaq Power Supply','AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ]
    
config_transfers = [
    [u'No Configuration Transfer','none'],
    [u'Cisco IOS, Newer than 12.0 (CONFIG-COPY-MIB)','cisco_cc'],
    [u'Cisco IOS, Older than 12.0 (SYS-MIB)','cisco_sys'],
    [u'Cisco CatOS, Catalyst Switches (STACK-MIB)','cisco_catos']
    ]

event_types = [
        # display_name, severity, tag, text, gen_alm, alm_up, alm_dur, show, sh_host
    [u'Unknown', u'Warning', 'unknown', u'$attribute $state $info',0,1,0,1,1],
    [u'Administrative', u'Administrative', 'admin', u'$attribute $info',1,1,1800,1,1],
    [u'SLA', u'Information', 'sla', u'$attribute $info (<client> ${description})',1,1,1800,1,1],
    [u'Internal', u'Information', 'internal', u'$user $attribute $state $info',0,1,0,1,0],

    [u'BGP Status', u'Critical', 'bgp_status', u'BGP Neighbor $attribute $state $info (<client> ${description})',1,1,0,1,1],
    [u'BGP Notification', u'Information', 'bgp_notify', u'Notification $state $attribute $info',0,1,0,1,1],

    [u'TCP/UDP Service', u'Service', 'tcpudp_service', u'TCP/UDP Service $attribute $state (<client> ${description}) $info',1,1,0,1,1],
    [u'TCP Content', u'Service', 'tcp_content', u'Content Response on $attribute is $state (<client> ${description}) $info',1,1,0,1,1],

    [u'Configuration', u'Warning', 'configuration', u'<user>: Changed Configuration from $info ${attribute}',0,1,0,1,1],
    [u'Interface Protocol', u'Fault', 'interface_protocol', u'Interface $attribute Protocol $state $info (<client> ${description})',1,1,0,1,1],
    [u'Interface Link', u'Big Fault', 'interface_link', u'Interface $attribute Link $state $info (<client> ${description})',0,1,0,1,1],
    [u'Controller Status', u'Big Fault', 'controller_status', u'Controller  $info $attribute $state',0,1,0,1,1],
    [u'Interface Shutdown', u'Big Fault', 'interface_shutdown', u'Interface $attribute $info $state (<client> ${description})',0,4,0,1,1],
    [u'Clear Counters', u'Information', 'clear_counters', u'<user> Cleared Counters of $attribute  (<client> ${description})',0,1,0,1,1],
    [u'Environmental', u'Critical', 'environment', u'$attribute $state $info',1,1,0,1,1],
    [u'Duplex Mismatch', u'Warning', 'duplex_mismatch', u'Duplex Mismatch, $attribute is not full duplex and <user> $info is full duplex',0,1,0,1,1],
    [u'ACL', u'Information', 'acl', u'ACL $attribute $state $info packets from <user>',0,1,0,1,1],
    [u'Excess Collisions', u'Warning', 'collision', u'Excess Collisions on Interface $attribute',0,1,0,1,1],
    [u'Application', u'Critical', 'application', u'Application $attribute is $state $info (<client> ${description})',1,1,0,1,1],
    [u'Reachability', u'Critical', 'reachability', u'Host is $state with $info',1,1,0,1,1],
    [u'NTP', u'Information', 'ntp', u'$attribute is $state $info',1,1,0,1,1],

    [u'APC Status', u'Critical', 'apc_status', u'$attribute is $state $info',1,1,0,1,1],

    [u'Alteon RServer', u'Fault', 'alteon_rserver', u'Real Server $attribute is $state',1,1,0,1,1],
    [u'Alteon Service', u'Fault', 'alteon_service', u'Real Service $attribute is $state $info',1,1,0,1,1],
    [u'Alteon VServer', u'Fault', 'alteon_vserver', u'Virtual Server $attribute is $state $info',0,1,0,1,1],

    [u'Brocade FC Port', u'Fault', 'brocade_fcport', u'$attribute $state ($info)',1,1,0,1,1],

    [u'OS/400 Error', u'Critical', 'os400_error', u'A subsystem is $state on the OS/400',1,1,0,1,1],
    [u'Storage Controller', u'Big Fault', 'storage_controller', u'$info',1,1,0,1,1]
    ]

event_severities = [
    [u'Unknown', 127, '000000', 'ffffff'],
    [u'Warning', 30, '00aa00', 'ffffff'],
    [u'Fault', 40, 'f51d30', 'eeeeee'],
    [u'Big Fault', 50, 'da4725','ffffff'],
    [u'Critical',60, 'ff0000', 'ffffff'],
    [u'Administrative',10, '8d00ba', 'ffffff'],
    [u'Information',20, 'f9fd5f', '000000'],
    [u'Service',35, '0090f0', 'ffffff']
    ]

logfiles = [
    [u'Database', u''],
    [u'Messages', u'/var/log/messages'],
    ]

logmatch_default_rows = [
        #text,start,host,attr,state,event_id,[fields]
        [u'%BGP-5-ADJCHANGE: neighbour (\S+) (\S+)$',
            True,None,1,2,'bgp_status',[]],
        [u'%BGP-3-NOTIFICATION: (\S+ \S+) neighbor (\S+) \S+ (\S+ \S+ \S+) \S+ \S+',
            True,None,2,1,'bgp_notify',[['info',3]]],
        [u'%CDP-4-DUPLEX_MISMATCH: duplex mismatch discovered on (\S+)',
            True,None,1,None,'duplex_mismatch',[]],
        [u'%CLEAR-5-COUNTERS: Clear counter on \S+ (\S+) by (\S+)',
            True,None,1,None,'clear_counters',[['user',2,]]],

        [u'%CONTROLLER-5-UPDOWN: Controller \S+ (\S+), changed state to (\S+) \([^)]+\)$',
            True,None,1,2,'controller_status',[['info',3]]],
        [u'%LINK-3-UPDOWN: Interface (\S+), changed state to (\S+)',
            True,None,1,2,'interface_link',[]],
        [u'%LINK-5-CHANGED: Interface (\S+) changed state to (\S+)',
            True,None,1,2,'interface_shutdown',[]],
        [u'%LINEPROTO-5-UPDOWN: Line protocol on Interface (\S+), changed to (\S+)',
            False,None,1,2,'interface_protocol',[]],
        [u'%SYS-5-CONFIG-(?:_I|): Configured from (\S+) by (\S+)$',
            True,None,None,None,'configuration',[['source',1],['proto',2]]],

        [u'%SYS-5-(?:RESTART|RELOAD): (.+)$',
            True,None,None,None,'environment',[['info',1]]],
        [u'%SEC-6-IPACCESSLOG(?:DP|P|NP|S): list (.+)$',
            True,None,None,None,'acl',[['info',1]]],
        [u'EXCESSCOLL: (\S+)',
            False,None,1,None,'collision',[]],
        [u'WebOS <slb>: No services are available for Virtual Server\d+:(\S+)',
            True,None,1,'down','alteon_vserver',[]],
        [u'UPS: ([^.]+)\. (.+)$',
            True,None,'UPS',None,'environment',[['info',1]]],
        [u'WebOS <slb>: real server (\S+) operational',
            True,None,1,'up','alteon_rserver',[]],
        [u'WebOS <slb>: cannot contact real server (\S+)',
            True,None,1,'down','alteon_rserver',[]],
        [u'WebOS <slb>: Services are available for Virtual Server\d+:(\S+)',
            True,None,1,'up','alteon_vserver',[]],
        [u'WebOS <slb>: real service (\S+) operational',
            True,None,1,'up','alteon_service',[]],
        [u'WebOS <slb>: cannot contact real service (\S+)',
            True,None,1,'down','alteon_service',[]],

    ]

slas = [
        [u'No SLA',3, u'No SLA',12,100,1, []],
        [u'Customer Satellite Link',3, u'Customer Sat Link:',12,75,4, [
            [15,1],
            [13,0],
            [4,0],
            [7,1],
            [18,1],
            [16,1],
            [6,0],
            [6,0],
            [5,0],
            [5,0],
            [6,0]
            ]],
        [u'Main Fiber Link',3, u'Main Link:',12,100,4, [
            [10,1],
            [12,1],
            [2,1],
            [15,1],
            [18,1],
            [6,0],
            [6,0],
            [6,0],
            [6,0],
            ]],
        [u'Main Satellite Link',3, u'Main Sat Link:',12,100,4, [
            [10,1],
            [12,1],
            [7,1],
            [3,1],
            [15,1],
            [6,0],
            [6,0],
            [6,0],
            [6,0],
            ]],
        [u'Cisco Router',3, u'Router:',12,100,3, [
            [22,1],
            [27,1],
            [6,0],
            ]],
        [u'Storage',3, u'Storage',12,100,8, [ [24,1],],],
        [u'Linux/Unix CPU',3, u'',12,100,11, [
            [25,1],
            [26,1],
            [6,0],
            ]],
        [u'Windows CPU',3, u'',12,100,12, [
            [28,1],
            [29,1],
            [6,0],
            ]],
        [u'APC UPS',3, u'APC UPS',12,100,31, [
            [31,1],
            [30,1],
            ]]
        ]

sla_conditions = [
        [u'None', '1', '=', 2, u'', '', u''],
        [u'Round Trip Time > 60ms', '$rtt', '>', 60, u'RTT > 60', u'$rtt', u'ms'],
        [u'Packet Loss > 20%', '$packetloss * 100 / $pings', '>', 20, u'PL > 20%', u'$packetloss * 100 / $pings', u'%'],
        [u'Input Traffic < 95%', '$in * 100 / $speed', '<', 95, u'IN < 95%', u'$in / 1000', u'kbps'],
        [u'AND', 'AND','=',0,u'', u'', u''],
        [u'OR', 'OR','=',0,u'', u'', u''],
        [u'Round Trip Time > 700ms', '$rtt', '>', 700, u'RTT > 700', u'$rtt', u'ms'],
        [u'Round Trip Time > 900ms', '$rtt', '>', 900, u'RTT > 900', u'$rtt', u'ms'],
        [u'Packet Loss > 50%', '$packetloss * 100 / $pings', '>', 50, u'PL > 50%', u'$packetloss * 100 / $pings', u'%'],
        # id 10 is missing
        [u'Input Traffic > 90%', '$in * 100 / $speed', '>', 90, u'IN > 90%', u'$in / 1000', u'kbps'],
        [u'Input Traffic < 1%', '$in * 100 / $speed', '<', 1, u'IN < 1%', u'$in / 1000', u'kbps'],
        [u'Output Traffic > 90%', '$out * 100 / $speed', '>', 90, u'IN > 90%', u'$out / 1000', u'kbps'],
        [u'Output Traffic < 95%', '$out * 100 / $speed', '<', 95, u'IN < 95%', u'$out / 1000', u'kbps'],
        [u'Input Error Rate > 20%', '($inerrors * 100) / ($inpackets + 1 )', '>', 20, u'IN ERR > 20%', u'($inerrors * 100) / ($inpackets + 1)', u'% = $inerrors Eps'],
        [u'Input Error Rate > 10%', '($inerrors * 100) / ($inpackets + 1 )', '>', 10, u'IN ERR > 10%', u'($inerrors * 100) / ($inpackets + 1)', u'% = $inerrors Eps'],
        #17 is missing
        [u'Drops > %1', '($drops * 100) / ($outpackets + 1)', '>', 1, u'Drops > 1%', u'($drops * 100) / ($outpackets + $drops + 1)', u'% = $drops dps'],
        [u'Drops > %2', '($drops * 100) / ($outpackets + 1)', '>', 2, u'Drops > 2%', u'($drops * 100) / ($outpackets + $drops + 1)', u'% = $drops dps'],
        [u'Packet Loss > 10%', '$packetloss * 100 / $pings', '>', 10, u'PL > 10%', u'$packetloss * 100 / $pings', u'%'],
        [u'Drops > %10', '($drops * 100) / ($outpackets + 1)', '>', 10, u'Drops > 10%', u'($drops * 100) / ($outpackets + $drops + 1)', u'% = $drops dps'],
        [u'Input Traffic < 99%', '$in * 100 / $speed', '<', 99, u'IN < 99%', u'$in / 1000', u'kbps'],
        [u'Output Traffic < 99%', '$out * 100 / $speed', '<', 99, u'IN < 99%', u'$out / 1000', u'kbps'],
        [u'High CPU Utilization', '$cpu - $cpu_threshold', '>', 0, u'Usage > $cpu_threshold', u'$cpu', u'%'],
        [u'Packet Loss > 10% SP', '$packetloss', '>', 10, u'PL > 10%', u'$packetloss', u'%'],
        [u'Used Storage', '($storage_used_blocks * 100) / $storage_block_count - $usage_threshold', '>', 0, u'Used > $usage_threshold', u'($storage_used_blocks * 100) / $storage_block_count', u'%'],
        [u'Load Average > 5', '$load_average_5', '>', 5, u'Load Average > 5', u'$load_average_5', u''],
        [u'High CPU Util (ticks)', '($cpu_user_ticks + $cpu_nice_ticks + $cpu_system_ticks) * 100 / ($cpu_user_ticks + $cpu_idle_ticks + $cpu_nice_ticks + $cpu_system_ticks) - $cpu_threshold', '>', 0, u'Usage > $cpu_threshold%', u'($cpu_user_ticks + $cpu_nice_ticks + $cpu_system_ticks) * 100 / ($cpu_user_ticks + $cpu_idle_ticks + $cpu_nice_ticks + $cpu_system_ticks)', u'%'],
        [u'Memory Usage > 80%', '$mem_used * 100 / ($mem_used + $mem_free)', '>', 80, 'Memory Usage > 80%', u'$mem_used * 100 / ($mem_used + $mem_free)', u'%'],
        [u'CPU Utilization > 90%', '$cpu', '>', 90, u'CPU > 90%', u'$cpu', u'%'],
        [u'Too Many Processes', '$num_procs - $proc_threshold', '>', 0, u'Processes > $proc_threshold', u'$num_procs', u'Processes'],
        [u'APC temp > 55', '$temperature - 55', '>', 0, u'APC temp > 55', u'$temperature', u'C'],
        [u'APC time < 50 minutes', '$time_remaining', '<', 30000, u'APC time < 50 minutes', u'$time_remaining / 6000', u'mins'
        ],
        ]

pollers = [
        ['no_poller','No Poller','no_poller',''],

        ['input','SNMP Input Rate','snmp_counter','1.3.6.1.2.1.31.1.1.1.6.${index}|1.3.6.1.2.1.2.2.1.10.${index}'],
        ['verify_interface_number','SNMP Verify Interface Number','verify_interface_number',''],
        ['cisco_snmp_ping_start','Cisco SNMP Ping Start','cisco_snmp_ping_start',''],
        ['cisco_snmp_ping_wait','Cisco SNMP Ping Wait','cisco_snmp_ping_wait',''],
        ['packetloss','Cisco SNMP Ping Get PL','cisco_snmp_ping_get_pl',''],
        ['rtt','Cisco SNMP Ping Get RTT','cisco_snmp_ping_get_rtt',''],
        ['cisco_snmp_ping_end','Cisco SNMP Ping End','cisco_snmp_ping_end',''],
        ['output','SNMP Output Rate','snmp_counter','1.3.6.1.2.1.31.1.1.1.10.${index}|1.3.6.1.2.1.2.2.1.16.${index}'],
        ['outputerrors','SNMP Output Errors','snmp_counter','1.3.6.1.2.1.2.2.1.20.${index}'],
        ['inputerrors','SNMP Input Errors','snmp_counter','1.3.6.1.2.1.2.2.1.14.${index}'],
        ['ifOper','SNMP Interface Operational Status','snmp_status','1.3.6.1.2.1.2.2.1.8.${index}|1=up,2=down,3=testing,4=unknown|down'],
        ['ifAdmin','SNMP Interface Administrative Status','snmp_status','1.3.6.1.2.1.2.2.1.7.${index}|1=up,2=down,3=testing,4=unknown|down'],
        ['cpu','Cisco CPU Utilization','snmp_counter','1.3.6.1.4.1.9.9.109.1.1.1.1.5.1'],
        ['inpackets','SNMP Input Packets','snmp_counter','1.3.6.1.2.1.31.1.1.1.7.${index}|1.3.6.1.2.1.2.2.1.11.${index}'],
        ['outpackets','SNMP Output Packets','snmp_counter','1.3.6.1.2.1.31.1.1.1.11.${index}|1.3.6.1.2.1.2.2.1.17.${index}'],
        ['tcp_status,tcp_content,conn_delay','TCP Port Check & Delay','tcp_status',''],
        ['mem_used','Cisco Used Memory','snmp_counter','1.3.6.1.4.1.9.9.48.1.1.1.5.1'],
        ['mem_free','Cisco Free Memory','snmp_counter','1.3.6.1.4.1.9.9.48.1.1.1.6.1'],
        ['drops','SNMP Drops','snmp_counter','1.3.6.1.2.1.2.2.1.19.${index}'],
        ['cpu','Cisco 2500 Series CPU Utilization','snmp_counter','1.3.6.1.4.1.9.2.1.56.0'],
        ['bgpin','BGP Inbound Updates','snmp_counter','1.3.6.1.2.1.15.3.1.10.${remote}'],
        ['bgpout','BGP Outbound Updates','snmp_counter','1.3.6.1.2.1.15.3.1.11.${remote}'],
        ['bgpuptime','BGP Uptime','snmp_counter','1.3.6.1.2.1.15.3.1.16.${remote}'],
        ['storage_used_blocks','Storage Device Used Blocks','snmp_counter','1.3.6.1.2.1.25.2.3.1.6.${index}'],
        ['storage_block_count','Storage Device Total Blocks','snmp_counter','1.3.6.1.2.1.25.2.3.1.5.${index}'],
        ['storage_block_size','Storage Device Block Size','snmp_counter','1.3.6.1.2.1.25.2.3.1.4.${index}'],
        ['bgp_peer_status','BGP Peer Status','snmp_status','1.3.6.1.2.1.15.3.1.2.${remote}|6=up|down'],
        ['cpu_kernel_ticks','CPU Kernel Time','snmp_counter','1.3.6.1.4.1.2021.11.55.0'],
        ['cpu_idle_ticks','CPU Idle Time','snmp_counter','1.3.6.1.4.1.2021.11.53.0'],
        ['cpu_wait_ticks','CPU Wait Time','snmp_counter','1.3.6.1.4.1.2021.11.54.0'],
        ['cpu_system_ticks','CPU System Time','snmp_counter','1.3.6.1.4.1.2021.11.52.0'],
        ['mem_available','Real Memory Available','snmp_counter','1.3.6.1.4.1.2021.4.6.0'],
        ['mem_total','Real Memory Total','snmp_counter','1.3.6.1.4.1.2021.4.5.0'],
        ['swap_available','Swap Memory Available','snmp_counter','1.3.6.1.4.1.2021.4.4.0'],
        ['swap_total','Swap Memory Total','snmp_counter','1.3.6.1.4.1.2021.4.3.0'],
        ['load_average_15','Load Average 15 min','snmp_counter','1.3.6.1.4.1.2021.10.1.3.3'],
        ['load_average_5','Load Average 5 min','snmp_counter','1.3.6.1.4.1.2021.10.1.3.2'],
        ['load_average_1','Load Average 1 min','snmp_counter','1.3.6.1.4.1.2021.10.1.3.1'],
        ['cpu_user_ticks','CPU User Time','snmp_counter','1.3.6.1.4.1.2021.11.50.0'],
        ['cpu_nice_ticks','CPU Nice Time','snmp_counter','1.3.6.1.4.1.2021.11.51.0'],
        ['tcp_established','TCP MIB Established','snmp_tcp_established',''],
        ['cpu','Host MIB Proc Average Util','snmp_walk_average','1.3.6.1.2.1.25.3.3.1.2'],
        ['num_procs','Host MIB Number of Processes','snmp_counter','1.3.6.1.2.1.25.1.6.0'],
        ['num_users','Host MIB Number of Users','snmp_counter','1.3.6.1.2.1.25.1.5.0'],
        ['tcp_active','TCP MIB Active Opens','snmp_counter','1.3.6.1.2.1.6.5.0'],
        ['tcp_passive','TCP MIB Passive Opens','snmp_counter','1.3.6.1.2.1.6.6.0'],
        ['tcp_established','TCP MIB Established Connections','snmp_counter','1.3.6.1.2.1.6.9.0'],
        ['app_status,current_instances,pids','Host MIB Process Verifier','hostmib_apps','${attribute}'],
        ['cisco_powersupply_status','Cisco Power Supply Status','snmp_status','1.3.6.1.4.1.9.9.13.1.5.1.3.${index}|1=up|down'],
        ['cisco_temperature_status','Cisco Temperature Status','snmp_status','1.3.6.1.4.1.9.9.13.1.3.1.6.${index}|1=up|down'],
        ['cisco_voltage_status','Cisco Voltage Status','snmp_status','1.3.6.1.4.1.9.9.13.1.2.1.7.${index}|1=up|down'],
        ['temperature','Cisco Temperature','snmp_counter','1.3.6.1.4.1.9.9.13.1.3.1.3.${index}'],
        ['sa_agent_verify','Verify SA Agent Operation','cisco_saagent_verify',''],
        ['forward_jitter','SA Agent Forward Jitter','cisco_saagent','${index}|fwd_jitter'],
        ['backward_jitter','SA Agent Backward Jitter','cisco_saagent','${index}|bwd_jitter'],
        ['rt_latency,forward_packetloss,backward_packetloss','SA Agent Packetloss','cisco_saagent','${index}|packetloss'],
        ['tcp_content_analisis','TCP Content Check','tcp_content',''],
        ['rtt,pl','Reachability Ping','reach_ping',''],
        ['status','Reachability Status','reach_status',''],
        ['tcp_status','TCP Port Status','buffer',''],
        ['app_status','Host MIB Status','buffer',''],
        ['ntp_status','NTP Status','ntp_client',''],
        ['used_memory','Host MIB Process Memory Usage','hostmib_perf','2'],
        ['udp_status,conn_delay','UDP Port Status & Delay','udp_status',''],
        ['udp_status','UDP Port Status','buffer',''],
        ['temperature','Compaq Temperature','snmp_counter','1.3.6.1.4.1.232.6.2.6.8.1.4.${chassis}.${tempindex}'],
        ['temp_status','Compaq Temperature Status','snmp_status','1.3.6.1.4.1.232.6.2.6.8.1.6.${chassis}.${tempindex}|2=up|down'],
        ['fan_status','Compaq Fan Condition','snmp_status','1.3.6.1.4.1.232.6.2.6.7.1.9.${chassis}.${fanindex}|2=up|down'],
        ['compaq_disk','Compaq Drive Condition','snmp_status','1.3.6.1.4.1.232.3.2.5.1.1.6.${controller}.${drvindex}|2=up|down'],
        ['tbr','IIS Total Bytes Received','snmp_counter','1.3.6.1.4.1.311.1.7.3.1.4.0'],
        ['tcgir','IIS Total CGI Requests','snmp_counter','1.3.6.1.4.1.311.1.7.3.1.35.0'],
        ['tfs','IIS Total Files Sent','snmp_counter','1.3.6.1.4.1.311.1.7.3.1.5.0'],
        ['tg','IIS Total GETs','snmp_counter','1.3.6.1.4.1.311.1.7.3.1.18.0'],
        ['tp','IIS Total Posts','snmp_counter','1.3.6.1.4.1.311.1.7.3.1.19.0'],
        ['tac,tkb,cplo,up,bpr,bw,iw','Apache Status','apache',''],
        ['capacity','APC Battery Capacity','snmp_counter','1.3.6.1.4.1.318.1.1.1.2.2.1.0'],
        ['load','APC Output Load','snmp_counter','1.3.6.1.4.1.318.1.1.1.4.2.3.0'],
        ['in_voltage','APC Input Voltage','snmp_counter','1.3.6.1.4.1.318.1.1.1.3.2.1.0'],
        ['out_voltage','APC Output Voltage','snmp_counter','1.3.6.1.4.1.318.1.1.1.4.2.1.0'],
        ['time_remaining','APC Time Remaining','snmp_counter','1.3.6.1.4.1.318.1.1.1.2.2.3.0'],
        ['status','APC Battery Status','snmp_status','1.3.6.1.4.1.318.1.1.1.2.1.1.0|2=battery normal,3=battery low|battery unknown'],
        ['temperature','APC Temperature','snmp_counter','1.3.6.1.4.1.318.1.1.1.2.2.2.0'],
        ['output_status','APC Output Status','snmp_status','1.3.6.1.4.1.318.1.1.1.4.1.1.0|2=on line,3=on battery'],
        ['admin_state','Alteon RServer Admin','snmp_counter','1.3.6.1.4.1.1872.2.1.5.2.1.10.${index}'],
        ['oper_state','Alteon RServer Oper','snmp_status','1.3.6.1.4.1.1872.2.1.9.2.2.1.7.${index}|2=up|down'],
        ['current_sessions','Alteon RServer Current Sessions','snmp_counter','1.3.6.1.4.1.1872.2.1.8.2.5.1.2.${index}'],
        ['failures','Alteon RServer Failures','snmp_counter','1.3.6.1.4.1.1872.2.1.8.2.5.1.4.${index}'],
        ['octets','Alteon RServer Octets','snmp_counter','1.3.6.1.4.1.1872.2.1.8.2.5.1.7.${index}'],
        ['total_sessions','Alteon RServer Total Sessions','snmp_counter','1.3.6.1.4.1.1872.2.1.8.2.5.1.3.${index}'],
        ['admin_state','Alteon VServer Admin State','snmp_counter','1.3.6.1.4.1.1872.2.1.5.5.1.4.${index}'],
        ['current_sessions','Alteon VServer Current Sessions','snmp_counter','1.3.6.1.4.1.1872.2.1.8.2.7.1.2.${index}'],
        ['total_sessions','Alteon VServer Total Sessions','snmp_counter','1.3.6.1.4.1.1872.2.1.8.2.7.1.3.${index}'],
        ['octets','Alteon VServer Octets','snmp_counter','.1.3.6.1.4.1.1872.2.1.8.2.7.1.6.${index}'],
        ['admin_state','Alteon RService Admin State','snmp_counter','1.3.6.1.4.1.1872.2.1.5.2.1.10.${real_server}'],
        ['oper_state','Alteon RService Oper State','snmp_status','1.3.6.1.4.1.1872.2.1.9.2.4.1.6.${index}|2=up|down'],
        ['response_time','Alteon RService Response Time','snmp_counter','1.3.6.1.4.1.1872.2.1.9.2.4.1.7.${index}'],
        ['cpua_1sec','Alteon CPU A 1Sec','snmp_counter','1.3.6.1.4.1.1872.2.1.8.16.1.0'],
        ['cpua_4secs','Alteon CPU A 4Secs','snmp_counter','1.3.6.1.4.1.1872.2.1.8.16.3.0'],
        ['cpua_64secs','Alteon CPU A 64Secs','snmp_counter','1.3.6.1.4.1.1872.2.1.8.16.5.0'],
        ['cpub_1sec','Alteon CPU B 1Sec','snmp_counter','1.3.6.1.4.1.1872.2.1.8.1.16.2.0'],
        ['cpub_4secs','Alteon CPU B 4Secs','snmp_counter','1.3.6.1.4.1.1872.2.1.8.16.4.0'],
        ['cpub_64secs','Alteon CPU B 64Secs','snmp_counter','1.3.6.1.4.1.1872.2.1.8.16.6.0'],
        ['mem_total','Alteon Memory Total','snmp_counter','1.3.6.1.4.1.1872.2.1.8.12.6.0'],
        ['mem_used','Alteon Memory Used','snmp_counter','1.3.6.1.4.1.1872.2.1.8.12.4.0'],
        ['sensor_value','Brocade Sensor Value','snmp_counter','1.3.6.1.4.1.1588.2.1.1.1.1.22.1.4.${index}'],
        ['oper_status','Brocade Sensor Oper','snmp_status','1.3.6.1.4.1.1588.2.1.1.1.1.22.1.3.${index}|4=ok,3=alert,5=alert'],
        ['tx_words','Brocade FC Port TxWords','snmp_counter','1.3.6.1.4.1.1588.2.1.1.1.6.2.1.11.${index}'],
        ['rx_words','Brocade FC Port RxWords','snmp_counter','1.3.6.1.4.1.1588.2.1.1.1.6.2.1.12.${index}'],
        ['tx_frames','Brocade FC Port TxFrames','snmp_counter','1.3.6.1.4.1.1588.2.1.1.1.6.2.1.13.${index}'],
        ['rx_frames','Brocade FC Port RxFrames','snmp_counter','1.3.6.1.4.1.1588.2.1.1.1.6.2.1.14.${index}'],
        ['admin_state','Brocade FC Port Admin State','snmp_counter','1.3.6.1.4.1.1588.2.1.1.1.6.2.1.5.${index}'],
        ['oper_status','Brocade FC Port Oper Status','snmp_status','1.3.6.1.4.1.1588.2.1.1.1.6.2.1.4.${index}|1=up,3=testing'],
        ['phy_state','Brocade FC Port Phy State','brocade_fcport_phystate','${index}'],
        ['status','UPS Battery Status','snmp_status','${ups_oid}.2.1.0|2=battery normal,1=battery unknown,3=battery low,3=battery depleted'],
        ['temperature','UPS Battery Temperature','snmp_counter','${ups_oid}.2.7.0'],
        ['minutes_remaining','UPS Battery Minutes Remaining','snmp_counter','${ups_oid}.2.3.0'],
        ['charge_remaining','UPS Battery Charge Remaining','snmp_counter','${ups_oid}.2.4.0'],
        ['voltage','UPS Input Voltage','snmp_counter','1.3.6.1.2.1.33.1.3.3.1.3.${index}'],
        ['current','UPS Input Current','snmp_counter','1.3.6.1.2.1.33.1.3.3.1.4.${index}'],
        ['voltage','UPS Output Voltage','snmp_counter','1.3.6.1.2.1.33.1.4.4.1.2.${index}'],
        ['current','UPS Output Current','snmp_counter','1.3.6.1.2.1.33.1.4.4.1.3.${index}'],
        ['load','UPS Output Load','snmp_counter','1.3.6.1.2.1.33.1.4.4.1.5.${index}'],
        ['voltage','Mitsu UPS Input Voltage','snmp_counter_mul','1.3.6.1.4.1.13891.101.3.3.1.3.${index}|0.1'],
        ['current','Mitsu UPS Input Current','snmp_counter_mul','1.3.6.1.4.1.13891.101.3.3.1.4.${index}|0.1'],
        ['power','Mitsu UPS Input Power','snmp_counter','1.3.6.1.4.1.13891.101.3.3.1.5.${index}'],
        ['voltage','Mitsu UPS Output Voltage','snmp_counter_mul','1.3.6.1.4.1.13891.101.4.4.1.2.${index}|0.1'],
        ['current','Mitsu UPS Output Current','snmp_counter_mul','1.3.6.1.4.1.13891.101.4.4.1.3.${index}|0.1'],
        ['power','Mitsu UPS Output Power','snmp_counter','1.3.6.1.4.1.13891.101.4.4.1.4.${index}'],
        ['load','Mitsu UPS Output Load','snmp_counter','1.3.6.1.4.1.13891.101.4.4.1.5.${index}'],
        ['accepted_routes','BGP Accepted Routes','snmp_counter','1.3.6.1.4.1.9.9.187.1.2.4.1.1.${remote}.1.1'],
        ['advertised_routes','BGP Advertised Routes','snmp_counter','1.3.6.1.4.1.9.9.187.1.2.4.1.6.${remote}.1.1'],
        ['pix_connections','Pix Connections Poller','snmp_counter','1.3.6.1.4.1.9.9.147.1.2.2.2.1.5.${index}'],
        ['cisco_nat_other_ip_inbound','Cisco NAT Other IP Inbound','snmp_counter','1.3.6.1.4.1.9.10.77.1.3.1.1.2.1'],
        ['cisco_nat_icmp_inbound','Cisco NAT ICMP Inbound','snmp_counter','1.3.6.1.4.1.9.10.77.1.3.1.1.2.2'],
        ['cisco_nat_udp_inbound','Cisco NAT UDP Inbound','snmp_counter','1.3.6.1.4.1.9.10.77.1.3.1.1.2.3'],
        ['cisco_nat_tcp_inbound','Cisco NAT TCP Inbound','snmp_counter','1.3.6.1.4.1.9.10.77.1.3.1.1.2.4'],
        ['cisco_nat_other_ip_outbound','Cisco NAT Other IP Outbound','snmp_counter','1.3.6.1.4.1.9.10.77.1.3.1.1.3.1'],
        ['cisco_nat_icmp_outbound','Cisco NAT ICMP Outbound','snmp_counter','1.3.6.1.4.1.9.10.77.1.3.1.1.3.2'],
        ['cisco_nat_udp_outbound','Cisco NAT UDP Outbound','snmp_counter','1.3.6.1.4.1.9.10.77.1.3.1.1.3.3'],
        ['cisco_nat_tcp_outbound','Cisco NAT TCP Outbound','snmp_counter','1.3.6.1.4.1.9.10.77.1.3.1.1.3.4'],
        ['cisco_nat_active_binds','Cisco NAT Active Binds','snmp_counter','1.3.6.1.4.1.9.10.77.1.2.1.0'],
        ['sensor_verify','Verify Sensor Index','verify_sensor_index',''],
        ['value','Sensor Value','snmp_counter','1.3.6.1.4.1.2021.13.16.${table_index}.1.3.${row_index}'],
        ['storage_verify','Verify Storage Index','verify_storage_index',''],
        ['cpu400','OS 400 System Load','snmp_counter','1.3.6.1.4.1.2.6.4.5.1.0'],
        ['dell_om_chassis','Dell OpenManage Chassis','snmp_status','1.3.6.1.4.1.674.10892.1.200.10.1.2.1|1=other,2=unknown,3=ok,4=noncritical,5=critical,6=nonrecoverabl|unknown'],
        ['dell_om_temp','Dell OpenManage Ambient Temp','snmp_counter','1.3.6.1.4.1.674.10892.1.700.20.1.6.1.1'],
        ['dell_om_fan_1','Dell OpenManage Fan RPM #1','snmp_counter','1.3.6.1.4.1.674.10892.1.700.12.1.6.1.1'],
        ['dell_om_fan_2','Dell OpenManage Fan RPM #2','snmp_counter','1.3.6.1.4.1.674.10892.1.700.12.1.6.1.2'],
        ['dell_om_fan_3','Dell OpenManage Fan RPM #3','snmp_counter','1.3.6.1.4.1.674.10892.1.700.12.1.6.1.3'],
        ['dell_om_fan_4','Dell OpenManage Fan RPM #4','snmp_counter','1.3.6.1.4.1.674.10892.1.700.12.1.6.1.4'],
        ['dell_om_fan_5','Dell OpenManage Fan RPM #5','snmp_counter','1.3.6.1.4.1.674.10892.1.700.12.1.6.1.5'],
        ['dell_om_fan_6','Dell OpenManage Fan RPM #6','snmp_counter','1.3.6.1.4.1.674.10892.1.700.12.1.6.1.6'],
        ['dell_om_fan_7','Dell OpenManage Fan RPM #7','snmp_counter','1.3.6.1.4.1.674.10892.1.700.12.1.6.1.7'],
        ['status','FC Oper Status','snmp_status','1.3.6.1.2.1.75.1.2.2.1.2.${index}|1=up,2=offline,4=linkFailure'],
        ['rx_frames','FCPort RxFrames','snmp_counter','1.3.6.1.2.1.75.1.4.3.1.1.${index}'],
        ['tx_frames','FCPort TxFrames','snmp_counter','1.3.6.1.2.1.75.1.4.3.1.2.${index}'],
        ['associated','802.11x Associated Clients','snmp_counter','1.3.6.1.4.1.9.9.273.1.1.2.1.1.1'],
        ['power_status','Compaq Power Condition','snmp_status','1.3.6.1.4.1.232.6.2.9.3.1.4.${chassis}.${bayindex}|2=up'],
        ['cur_disk_q','Inf-64 Disk CurrentDiskQueue','snmp_counter','1.3.6.1.4.1.9600.1.2.44.1.16.${index}'],
        ['avg_disk_q','Inf-64 Disk AvgDiskQueu','snmp_counter','1.3.6.1.4.1.9600.1.2.44.1.10.${index}'],
        ['avg_disk_rdq','Inf-64 Disk avg Read DiskQueue','snmp_counter','1.3.6.1.4.1.9600.1.2.44.1.11.${index}'],
        ['avg_disk_wrq','Inf-64 Disk avg Write DiskQueue','snmp_counter','1.3.6.1.4.1.9600.1.2.44.1.12.${index}'],
        ['inf_d_read_time','Inf-64 Disk Read Time','snmp_counter','1.3.6.1.4.1.9600.1.2.44.1.2.${index}'],
        ['inf_d_write_time','Inf-64 Disk Write Time','snmp_counter','1.3.6.1.4.1.9600.1.2.44.1.4.${index}'],
        ['rd_ops','Inf-64 Disk Read rate','snmp_counter','1.3.6.1.4.1.9600.1.2.44.1.19.${index}'],
        ['wr_ops','Inf-64 Disk Write rate','snmp_counter','1.3.6.1.4.1.9600.1.2.44.1.22.${index}'],
        ['inf_d_read_rate','Inf-64 Disk Read Bytes','snmp_counter','1.3.6.1.4.1.9600.1.2.44.1.18.${index}'],
        ['inf_d_write_rate','Inf-64 Disk Write Bytes','snmp_counter','1.3.6.1.4.1.9600.1.2.44.1.21.${index}'],
        ]

backends = [
        [u'No Backend','',''],
        [u'Unknown Event','event_always','unknown'],
        [u'Alarm APC','event','apc_status'],
        [u'Alarm BGP Peer','event','bgp_status,,180'],
        [u'Alarm Brocade FC Port','event','brocade_fcport'],
        [u'Alarm Environmental','event','environment'],
        [u'Alarm NTP','event','ntp,nothing'],
        [u'Set Admin Status','admin_status','down=2|up=1,0'],
        [u'Alarm TCP Content','event','tcp_content'],
        [u'Alarm TCP Port','event','tcpudp_service'],
        [u'Alarm Verify Operational','event','interface_protocol,,180'],
        [u'Alarm Reachability','event','reachability'],
        [u'Application Alarm','event','application'],
        [u'Alteon Admin Status','admin_status','down=0|up=2,2'],
        [u'Alarm Alteon RServer','event','alteon_rserver'],
        [u'Alarm Alteon Service','event','alteon_service'],
        [u'Alarm Alteon VServer','event','alteon_vserver'],
        [u'Brocade FC Admin View','admin_status','down=2|up=1,0'],
        [u'Change Interface Number','verify_index',''],
        [u'Alarm OS/400','event','os400_error'],
        ]

poller_sets = [
        [u'No Poller', u'No Interface Type', []],
        [u'Cisco Interface', u'Physical Interfaces', [
            [u'SNMP Verify Interface Number', u'Change Interface Number'],
            [u'Cisco SNMP Ping Start', u''],
            [u'SNMP Interface Operational Status', u'Alarm Verify Operational'],
            [u'SNMP Interface Administrative Status', u'Set Admin Status'],
            [u'SNMP Input Rate', u''],
            [u'SNMP Input Packets', u''],
            [u'SNMP Output Rate', u''],
            [u'SNMP Output Packets', u''],
            [u'SNMP Output Errors', u''],
            [u'SNMP Input Errors', u''],
            [u'SNMP Drops', u''],
            [u'Cisco SNMP Ping Wait', u''],
            [u'Cisco SNMP Ping Get PL', u''],
            [u'Cisco SNMP Ping Get RTT', u''],
            [u'Cisco SNMP Ping End', u''],
            ]],
        [u'Cisco Router', u'Cisco System Info', [
            [u'Cisco CPU Utilization', u''],
            [u'TCP MIB Established Connections', u''],
            [u'Cisco Used Memory', u''],
            [u'TCP MIB Active Opens', u''],
            [u'Cisco Free Memory', u''],
            [u'TCP MIB Passive Opens', u''],
            ]],
        [u'TCP/IP Port', u'TCP Ports', [
            [u'TCP Port Check & Delay', u''],
            [u'TCP Port Status', u'Alarm TCP Port'],
            [u'TCP MIB Established', u''],
            [u'TCP Content Check', u'Alarm TCP Content']
            ]],
        [u'BGP Neighbor', u'BGP Neighbors', [
            [u'BGP Peer Status', u'Alarm BGP Peer' ],
            [u'BGP Inbound Updates', u''],
            [u'BGP Accepted Routes', u''],
            [u'BGP Advertised Routes', u''],
            [u'BGP Outbound Updates', u''],
            [u'BGP Uptime', u'']
            ]],
        [u'Storage Device', u'Storage', [
            [u'Verify Storage Index', u'Change Interface Number'],
            [u'Storage Device Block Size', u''],
            [u'Storage Device Total Blocks', u''],
            [u'Storage Device Used Blocks', u'']
            ]],
        [u'Linux/Unix Host', u'Linux/Unix System Info', [
            [u'CPU Nice Time', u''],
            [u'Host MIB Number of Processes', u''],
            [u'CPU User Time', u''],
            [u'Host MIB Number of Users', u''],
            [u'CPU Idle Time', u''],
            [u'TCP MIB Established Connections', u''],
            [u'CPU System Time', u''],
            [u'TCP MIB Active Opens', u''],
            [u'Load Average 1 min', u''],
            [u'TCP MIB Passive Opens', u''],
            [u'Load Average 5 min', u''],
            [u'Load Average 15 min', u'']
            ]],
        [u'Solaris Host', u'Solaris System Info', [
            [u'CPU System Time', u''],
            [u'CPU Idle Time', u''],
            [u'CPU Kernel Time', u''],
            [u'CPU Wait Time', u''],
            [u'Load Average 1 min', u''],
            [u'Load Average 5 min', u''],
            [u'Load Average 15 min', u''],
            [u'Real Memory Available', u''],
            [u'Real Memory Total', u''],
            [u'Swap Memory Available', u''],
            [u'Swap Memory Total', u''],
            ]],
        [u'Windows Host', u'Windows System Info', [
            [u'Host MIB Proc Average Util', u''],
            [u'Host MIB Number of Processes', u''],
            [u'Host MIB Number of Users', u''],
            [u'TCP MIB Active Opens', u''],
            [u'TCP MIB Established Connections', u''],
            [u'TCP MIB Passive Opens', u'']
            ]],
        [u'HostMIB Application', u'Applications', [
            [u'Host MIB Process Verifier', u''],
            [u'Host MIB Status', u'Application Alarm'],
            [u'Host MIB Process Memory Usage', u'']
            ]],
        [u'Cisco Power Supply', u'Cisco Power Supply', [
            [u'Cisco Power Supply Status', u'Alarm Environmental'],
            ]],
        [u'Cisco Temperature', u'Cisco Temperature', [
            [u'Cisco Temperature Status', u'Alarm Environmental'],
            [u'Cisco Temperature', u'']
            ]],
        [u'Cisco Voltage', u'Cisco Voltage', [
            [u'Cisco Voltage Status', u'Alarm Environmental'],
            ]],
        [u'Cisco SA Agent', u'Cisco SA Agent', [
            [u'SA Agent Forward Jitter', u''],
            [u'SA Agent Backward Jitter', u''],
            [u'SA Agent Packetloss', u''],
            ]],
        [u'Reachability', u'Reachable', [
            [u'Reachability Ping', u''],
            [u'Reachability Status', u'Alarm Reachability'],
            ]],
        [u'NTP', u'NTP', [
            [u'NTP Status', u'Alarm NTP'],
            ]],
        [u'UDP/IP Port', u'UDP Ports', [
            [u'UDP Port Status & Delay', u''],
            [u'UDP Port Status', u'Alarm TCP Port']
            ]],
        [u'Compaq Physical Drive', u'Compaq Physical Drives', [
            [u'Compaq Drive Condition', u'Alarm Environmental'],
            ]],
        [u'Compaq Fan', u'Compaq Fans', [
            [u'Compaq Fan Condition', u'Alarm Environmental'],
            ]],
        [u'Compaq Temperature', u'Compaq Temperature', [
            [u'Compaq Temperature Status', u'Alarm Environmental'],
            [u'Compaq Temperature', u'']
            ]],
        [u'IIS Info', u'IIS Webserver Information', [
            [u'IIS Total Bytes Received', u''],
            [u'IIS Total CGI Requests', u''],
            [u'IIS Total Files Sent', u''],
            [u'IIS Total GETs', u''],
            [u'IIS Total Posts', u'']
            ]],
        [u'Apache', u'Apache', [
            [u'Apache Status', u''],
            ]],
        [u'APC', u'APC', [
            [u'APC Battery Status', u'Alarm Environmental' ],
            [u'APC Output Status', u'Alarm APC' ],
            [u'APC Battery Capacity', u''],
            [u'APC Output Load', u''],
            [u'APC Input Voltage', u''],
            [u'APC Output Voltage', u''],
            [u'APC Time Remaining', u''],
            [u'APC Temperature', u'']
            ]],
        [u'Alteon Real Server', u'Alteon Real Server', [
            [u'Alteon RServer Admin', u'Alteon Admin Status'],
            [u'Alteon RServer Oper', u'Alarm Verify Operational'],
            [u'Alteon RServer Current Sessions', u''],
            [u'Alteon RServer Failures', u''],
            [u'Alteon RServer Octets', u''],
            [u'Alteon RServer Total Sessions', u'']
            ]],
        [u'Alteon Virtual Server', u'Alteon Virtual Server', [
            [u'Alteon VServer Admin State', u'Set Admin Status'],
            [u'Alteon VServer Current Sessions', u''],
            [u'Alteon VServer Octets', u''],
            [u'Alteon VServer Total Sessions', u'']
            ]],
        [u'Alteon Real Services', u'Alteon Real Services', [
            [u'Alteon RService Admin State', u'Set Admin Status'],
            [u'Alteon RService Oper State', u'Alarm Alteon Service'],
            [u'Alteon RService Response Time', u'']
            ]],
        [u'Alteon System Info', u'Alteon System Info', [
            [u'Alteon CPU A 1Sec', u''],
            [u'Alteon CPU A 4Secs', u''],
            [u'Alteon CPU A 64Secs', u''],
            [u'Alteon CPU B 1Sec', u''],
            [u'Alteon CPU B 4Secs', u''],
            [u'Alteon CPU B 64Secs', u''],
            [u'TCP MIB Active Opens', u''],
            [u'TCP MIB Passive Opens', u''],
            [u'TCP MIB Established Connections', u''],
            [u'Alteon Memory Used', u''],
            [u'Alteon Memory Total', u'']
            ]],
        [u'Brocade Sensors', u'Brocade Sensors', [
            [u'Brocade Sensor Oper', u'Alarm Verify Operational'],
            [u'Brocade Sensor Value', u''],
            ]],
        [u'Brocade FC Ports', u'Brocade FC Ports', [
            [u'Brocade FC Port Admin State', u'Brocade FC Admin View'],
            [u'Brocade FC Port Oper Status', u'Alarm Verify Operational'],
            [u'Brocade FC Port Phy State', u'Alarm Brocade FC Port'],
            [u'Brocade FC Port TxWords', u''],
            [u'Brocade FC Port RxWords', u''],
            [u'Brocade FC Port TxFrames', u''],
            [u'Brocade FC Port RxFrames', u'']
            ]],
        [u'UPS', u'UPS', [
            [u'UPS Battery Status', u'Alarm Environmental'],
            [u'UPS Battery Charge Remaining', u''],
            [u'UPS Battery Minutes Remaining', u''],
            [u'UPS Battery Temperature', u'']
            ]],
        [u'UPS Input Line', u'UPS Input Line', [
            [u'UPS Input Voltage', u''],
            [u'UPS Input Current', u''],
            ]],
        [u'UPS Output Line', u'UPS Output Line', [
            [u'UPS Output Voltage', u''],
            [u'UPS Output Current', u''],
            [u'UPS Output Load', u''],
            ]],
        [u'Mitsubishi UPS Input Line', u'Mitsubishi UPS Input Line', [
            [u'Mitsu UPS Input Voltage', u''],
            [u'Mitsu UPS Input Current', u''],
            [u'Mitsu UPS Input Power', u''],
            ]],
        [u'Mitsubishi UPS Output Line', u'Mitsubishi UPS Output Line', [
            [u'Mitsu UPS Output Voltage', u''],
            [u'Mitsu UPS Output Current', u''],
            [u'Mitsu UPS Output Load', u''],
            [u'Mitsu UPS Output Power', u'']
            ]],
        [u'PIX Connection Stat', u'Cisco PIX', [
            [u'Pix Connections Poller', u''],
            ]],
        [u'Cisco NAT', u'Cisco NAT', [
            [u'Cisco NAT Other IP Outbound', u''],
            [u'Cisco NAT Other IP Inbound', u''],
            [u'Cisco NAT ICMP Outbound', u''],
            [u'Cisco NAT ICMP Inbound', u''],
            [u'Cisco NAT UDP Outbound', u''],
            [u'Cisco NAT UDP Inbound', u''],
            [u'Cisco NAT TCP Outbound', u''],
            [u'Cisco NAT TCP Inbound', u''],
            [u'Cisco NAT Active Binds', u'']
            ]],
        [u'Sensors', u'Sensors', [
            [u'Verify Sensor Index', u'Change Interface Number'],
            [u'Sensor Value', u''],
            ]],
        [u'OS/400 Host', u'OS/400 System Info', [
            [u'OS 400 System Load', u''],
            ]],
        [u'Dell Chassis', u'Dell Chassis', [
            [u'Dell OpenManage Chassis', u'Alarm Verify Operational'],
            [u'Dell OpenManage Chassis' ,u'Set Admin Status'],
            [u'Dell OpenManage Ambient Temp', u''],
            [u'Dell OpenManage Fan RPM #1', u''],
            [u'Dell OpenManage Fan RPM #2', u''],
            [u'Dell OpenManage Fan RPM #3', u''],
            [u'Dell OpenManage Fan RPM #4', u''],
            [u'Dell OpenManage Fan RPM #5', u''],
            [u'Dell OpenManage Fan RPM #6', u''],
            [u'Dell OpenManage Fan RPM #7', u''],
            ]],
        [u'Compaq Power Supply', u'Compaq Power Supply', [
            [u'Compaq Power Condition', u'Alarm Environmental'],
            ]],
        [u'Cisco 802.11X Device', u'Cisco 802.11X Device', [
            [u'802.11x Associated Clients', u''],
            ]],
        [u'Fibre Channel Interface', u'Generic FC Ports', [
            [u'FC Oper Status', u'Alarm Environmental'],
            [u'FCPort RxFrames', u''],
            [u'FCPort TxFrames', u''],
            ]],
        [u'SNMP Interface', u'Physical Interfaces', [
            [u'SNMP Verify Interface Number', u'Change Interface Number'],
            [u'SNMP Interface Operational Status', u'Alarm Verify Operational'],
            [u'SNMP Interface Administrative Status', u'Set Admin Status'],
            [u'SNMP Input Rate', u''],
            [u'SNMP Input Packets', u''],
            [u'SNMP Output Rate', u''],
            [u'SNMP Output Packets', u''],
            [u'SNMP Output Errors', u''],
            [u'SNMP Input Errors', u''],
            [u'SNMP Drops', u''],
            ]],
        ]

graph_types = [
        [u'Traffic', 'Physical Interfaces', '', u'bps', '',
            [ #DEF
                ['input', 'input'],
                ['output', 'output'],
            ],[ #vnames
                ['CDEF', 'inputbits', 'input,UN,input,input,IF,8,*'],
                ['CDEF', 'outputbits', 'output,UN,output,output,IF,8,*'],
                ['VDEF', 'inputmax', 'inputbits,MAXIMUM'],
                ['VDEF', 'inputavg', 'inputbits,AVERAGE'],
                ['VDEF', 'inputlast', 'inputbits,LAST'],
                ['VDEF', 'outputmax', 'outputbits,MAXIMUM'],
                ['VDEF', 'outputavg', 'outputbits,AVERAGE'],
                ['VDEF', 'outputlast', 'outputbits,LAST'],
            ],[ #lines
                ['HRULE', 'speed', 'CC0000', 'Bandwidth ${speed_units}bps\l'],
                ['AREA', 'inputbits', '00CC00', ' Inbound\\n', False],
                ['PRINT', 'inputmax', 'Max: %6.2lf%S'],
                ['PRINT', 'inputavg', 'Avg: %6.2lf%S'],
                ['PRINT', 'inputlast', r'Cur: %6.2lf%S\l'],
                ['LINE', 'outputbits', '0000CC', 2, 'Outbound (bps)'],
                ['PRINT', 'outputmax', 'Max: %6.2lf%S'],
                ['PRINT', 'outputavg', 'Avg: %6.2lf%S'],
                ['PRINT', 'outputlast', 'Cur: %6.2lf%S\l'],
            ] ],
        [u'Utilization', 'Physical Interfaces', 'Utilization', u'%', '',
            [ #DEF
                ['input', 'input'],
                ['output', 'output'],
            ],[ #vnames
                ['CDEF', 'input_pct', 'input,UN,0,input,IF,800,*,$speed,/'],
                ['CDEF', 'output_pct', 'output,UN,0,output,IF,800,*,$speed,/'],
                ['VDEF', 'inputmax', 'input_pct,MAXIMUM'],
                ['VDEF', 'inputavg', 'input_pct,AVERAGE'],
                ['VDEF', 'inputlast', 'input_pct,LAST'],
                ['VDEF', 'outputmax', 'output_pct,MAXIMUM'],
                ['VDEF', 'outputavg', 'output_pct,AVERAGE'],
                ['VDEF', 'outputlast', 'output_pct,LAST'],
            ],[ #lines
                ['HRULE', '100', 'CC0000', None],
                ['AREA', 'input_pct', '00CC00', ' Input\\n', False],
                ['PRINT', 'inputmax', 'Max: %5.1lf%%'],
                ['PRINT', 'inputavg', 'Avg: %5.1lf%%'],
                ['PRINT', 'inputlast', r'Cur: %5.1lf%%\l'],
                ['LINE', 'output_pct', '0000CC', 2, 'Output'],
                ['PRINT', 'outputmax', 'Max: %5.1lf%%'],
                ['PRINT', 'outputavg', 'Avg: %5.1lf%%'],
                ['PRINT', 'outputlast', 'Cur: %5.1lf%%\l'],
            ] ],
        [u'Packets', 'Physical Interfaces', '', u'Pps', '',
            [ #DEF
                ['input', 'inpackets'],
                ['output', 'outpackets'],
            ],[ #vnames
                ['VDEF', 'inputmax', 'input,MAXIMUM'],
                ['VDEF', 'inputavg', 'input,AVERAGE'],
                ['VDEF', 'inputlast', 'input,LAST'],
                ['VDEF', 'outputmax', 'output,MAXIMUM'],
                ['VDEF', 'outputavg', 'output,AVERAGE'],
                ['VDEF', 'outputlast', 'output,LAST'],
            ],[ #lines
                ['AREA', 'input', '00CC00', ' Input Packets\n', False],
                ['PRINT', 'inputmax', 'Max: %6.2lf%S'],
                ['PRINT', 'inputavg', 'Avg: %6.2lf%S'],
                ['PRINT', 'inputlast', r'Cur: %6.2lf%S\l'],
                ['LINE', 'output', '0000CC', 2, 'Output Packets'],
                ['PRINT', 'outputmax', 'Max: %6.2lf%S'],
                ['PRINT', 'outputavg', 'Avg: %6.2lf%S'],
                ['PRINT', 'outputlast', 'Cur: %6.2lf%S\l'],
            ] ],
        [u'Packets New', 'Physical Interfaces', '', u'Pps', '',
            [ #DEF
                ['inpackets', 'inpackets'],
                ['outpackets', 'outpackets'],
                ['inputerrors', 'inputerrors'],
                ['outputerrors', 'outputerrors'],
            ],[ #vnames
                ['CDEF', 'input', 'inpackets,UN,0,inpackets,IF'],
                ['CDEF', 'output', 'outpackets,UN,0,outpackets,IF'],
                ['CDEF', 'inputerr', 'inputerrors,UN,0,inputerrors,IF'],
                ['CDEF', 'outputerr', 'outputerrors,UN,0,outputerrors,IF'],
                ['CDEF', 'outputrev', 'output,-1,*'],
                ['CDEF', 'totin', 'input,inputerr,+'],
                ['CDEF', 'totout', 'output,outputerr,+'],

                ['CDEF', 'inpct1', 'input,100,*,totin,/'],
                ['CDEF', 'outpct1', 'output,100,*,totout,/'],

                ['CDEF', 'inpct', 'inpct1,UN,100,inpct1,IF'],
                ['CDEF', 'outpct', 'outpct1,UN,100,outpct1,IF'],

                ['CDEF', 'ierrpct1', 'inputerr,100,*,totin,/,0.01,100,LIMIT'],
                ['CDEF', 'oerrpct1', 'outputerr,100,*,totout,/,0.01,100,LIMIT'],

                ['CDEF', 'ierrpct', 'ierrpct1,UN,0,ierrpct1,IF'],
                ['CDEF', 'oerrpct', 'oerrpct1,UN,0,oerrpct1,IF'],

                ['VDEF', 'inputmax', 'input,MAXIMUM'],
                ['VDEF', 'inputavg', 'input,AVERAGE'],
                ['VDEF', 'inputlast', 'input,LAST'],
                ['VDEF', 'inpctmax', 'inpct,MAXIMUM'],
                ['VDEF', 'inpctavg', 'inpct,AVERAGE'],
                ['VDEF', 'inpctlast', 'inpct,LAST'],

                ['VDEF', 'inerrmax', 'inputerr,MAXIMUM'],
                ['VDEF', 'inerravg', 'inputerr,AVERAGE'],
                ['VDEF', 'inerrlast', 'inputerr,LAST'],
                ['VDEF', 'inerrpctmax', 'ierrpct,MAXIMUM'],
                ['VDEF', 'inerrpctavg', 'ierrpct,AVERAGE'],
                ['VDEF', 'inerrpctlast', 'ierrpct,LAST'],

                ['VDEF', 'outputmax', 'output,MAXIMUM'],
                ['VDEF', 'outputavg', 'output,AVERAGE'],
                ['VDEF', 'outputlast', 'output,LAST'],
                ['VDEF', 'outpctmax', 'outpct,MAXIMUM'],
                ['VDEF', 'outpctavg', 'outpct,AVERAGE'],
                ['VDEF', 'outpctlast', 'outpct,LAST'],

                ['VDEF', 'outerrmax', 'outputerr,MAXIMUM'],
                ['VDEF', 'outerravg', 'outputerr,AVERAGE'],
                ['VDEF', 'outerrlast', 'outputerr,LAST'],
                ['VDEF', 'outerrpctmax', 'oerrpct,MAXIMUM'],
                ['VDEF', 'outerrpctavg', 'oerrpct,AVERAGE'],
                ['VDEF', 'outerrpctlast', 'oerrpct,LAST'],
            ],[ #lines
                ['AREA', 'input', '00CC00', 'Input  Packets\n', False],
                ['PRINT', 'inputmax', r'%6.2lf%S\g'],
                ['PRINT', 'inpctmax', '(%5.1lf%%)\g'],
                ['PRINT', 'inputavg', r'%6.2lf%S\g'],
                ['PRINT', 'inpctavg', '(%5.1lf%%)\g'],
                ['PRINT', 'inputlast', r'%6.2lf%S\g'],
                ['PRINT', 'inpctlast', '(%5.1lf%%)\j'],
                ['AREA', 'ierrpct', 'FF0000', r'Input  Errors \g', True],
                ['PRINT', 'inerrmax', r'%6.2lf%S\g'],
                ['PRINT', 'inerrpctmax', '(%5.1lf%%)\g'],
                ['PRINT', 'inerravg', r'%6.2lf%S\g'],
                ['PRINT', 'inerrpctavg', '(%5.1lf%%)\g'],
                ['PRINT', 'inerrlast', r'%6.2lf%S\g'],
                ['PRINT', 'inerrpctlast', '(%5.1lf%%)\j'],

                ['AREA', 'outputrev', '0000FF', 'Output Packets\n', False],
                ['PRINT', 'outputmax', '%6.2lf%S\g'],
                ['PRINT', 'outpctmax', '(%5.1lf%%)\g'],
                ['PRINT', 'outputavg', '%6.2lf%S\g'],
                ['PRINT', 'outpctavg', '(%5.1lf%%)\g'],
                ['PRINT', 'outputlast', '%6.2lf%S\g'],
                ['PRINT', 'outpctlast', '(%5.1lf%%)\j'],
                ['AREA', 'oerrpct', 'AA0000', 'Output Errors \g', True],
                ['PRINT', 'outerrmax', '%6.2lf%S\g'],
                ['PRINT', 'outerrpctmax', '(%5.1lf%%)\g'],
                ['PRINT', 'outerravg', '%6.2lf%S\g'],
                ['PRINT', 'outerrpctavg', '(%5.1lf%%)\g'],
                ['PRINT', 'outerrlast', '%6.2lf%S\g'],
                ['PRINT', 'outerrpctlast', '(%5.1lf%%)\j'],

            ] ],
        [u'Errors', 'Physical Interfaces', '', u'Errors/sec', '',
            [ #DEF
                ['input', 'inputerrors'],
                ['output', 'outputerrors'],
            ],[ #vnames
                ['VDEF', 'inputavg', 'input,AVERAGE'],
                ['VDEF', 'inputlast', 'input,LAST'],
                ['VDEF', 'outputavg', 'output,AVERAGE'],
                ['VDEF', 'outputlast', 'output,LAST'],
            ],[ #lines
                ['AREA', 'input', '00CC00', ' Input Errors\\n', False],
                ['PRINT', 'inputavg', 'Input Errors :- Average: %4.0lf %sEps'],
                ['PRINT', 'inputlast', r'Current: %4.0lf %sEps\l'],
                ['LINE', 'output', '0000CC', 2, 'Output Errors'],
                ['PRINT', 'outputavg', 'Output Errors :- Average: %4.0lf %sEps'],
                ['PRINT', 'outputlast', 'Current: %4.0lf %sEps\l'],
            ] ],
        
            
        [u'Hits', 'Apache', '', u'Hits', '',
            [ #DEF
                ['tac', 'tac'],
            ],[ #vnames
                ['VDEF', 'tacmax', 'tac,MAXIMUM'],
                ['VDEF', 'tacavg', 'tac,AVERAGE'],
                ['VDEF', 'taclast', 'tac,LAST'],
            ],[ #lines
                ['LINE', 'tac', '0000CC', 2, 'Hits per Second'],
                ['PRINT', 'tacmax', 'Maximum: %8.0lf %sHits/s'],
                ['PRINT', 'tacavg', 'Average: %8.0lf %sHits/s'],
                ['PRINT', 'taclast', 'Current: %8.0lf %sHits/s\l'],
            ]
        ],
        [u'Throughput', 'Apache', '', u'Bytes/Sec', '',
            [ #DEF
                ['tkb', 'tkb'],
            ],[ #vnames
                ['CDEF', 'bytes', 'tkb,1000,*'],
                ['VDEF', 'bytesmax', 'bytes,MAXIMUM'],
                ['VDEF', 'bytesavg', 'bytes,AVERAGE'],
                ['VDEF', 'byteslast', 'bytes,LAST'],
            ],[ #lines
                ['LINE', 'bytes', '0000CC', 2, ''],
                ['PRINT', 'bytesmax', 'Maximum: %8.0lf %sBps'],
                ['PRINT', 'bytesavg', 'Average: %8.0lf %sBps'],
                ['PRINT', 'byteslast', 'Current: %8.0lf %sBps\l'],
            ]
        ],
        [u'CPU Load', 'Apache', '', u'Bytes/Sec', '',
            [ #DEF
                ['up', 'up'],
                ['load', 'cplo'],
            ],[ #vnames
                ['VDEF', 'loadmax', 'load,MAXIMUM'],
                ['VDEF', 'loadavg', 'load,AVERAGE'],
                ['VDEF', 'loadlast', 'load,LAST'],
                ['VDEF', 'uplast', 'up,LAST'],
            ],[ #lines
                ['LINE', 'load', '0000CC', 2, ''],
                ['PRINT', 'uplast', 'Uptime  -  %.0lf %s seconds\l'],
                ['PRINT', 'loadmax', 'CPU Load - Maximum: %.3lf'],
                ['PRINT', 'loadavg', 'Average: %.3lf'],
                ['PRINT', 'loadlast', 'Current: %.3lf\l'],
            ]
        ],
        [u'Bytes/Req', 'Apache', '', u'Bytes/Req', '',
            [ #DEF
                ['bpr', 'bpr'],
            ],[ #vnames
                ['VDEF', 'bprmax', 'bpr,MAXIMUM'],
                ['VDEF', 'bpravg', 'bpr,AVERAGE'],
                ['VDEF', 'bprlast', 'bpr,LAST'],
            ],[ #lines
                ['LINE', 'bpr', '0000CC', 2, 'Bytes/Request'],
                ['PRINT', 'bprmax', 'Maximum: %.0lf %s'],
                ['PRINT', 'bpravg', 'Average: %.0lf %s'],
                ['PRINT', 'bprlast', 'Current: %.0lf %s\l'],
            ]
        ],
        [u'Workers', 'Apache', '', u'Workers', 'lower-limit=0',
            [ #DEF
                ['bw', 'bw'],
                ['iw', 'iw'],
            ],[ #vnames
                ['VDEF', 'bwmax', 'bw,MAXIMUM'],
                ['VDEF', 'bwavg', 'bw,AVERAGE'],
                ['VDEF', 'bwlast', 'bw,LAST'],
                ['VDEF', 'iwmax', 'iw,MAXIMUM'],
                ['VDEF', 'iwavg', 'iw,AVERAGE'],
                ['VDEF', 'iwlast', 'iw,LAST'],
            ],[ #lines
                ['HRULE', '0', '000000', ''],
                ['AREA', 'bw', 'DD2200', r'Busy Workers\l'],
                ['AREA', 'iw', '00CC00', 'Idle Workers\l', True],
                ['PRINT', 'bwmax', r'Workers (busy:idle) - Maximum: %.0lf:\g'],
                ['PRINT', 'iwmax', r'%.0lf'],
                ['PRINT', 'bwavg', r'Average: %.0lf:\g'],
                ['PRINT', 'iwavg', r'%.0lf'],
                ['PRINT', 'bwlast', r'Current: %.0lf:\g'],
                ['PRINT', 'iwlast', r'%.0lf'],
            ]
        ],
        
        [u'Sensor Value', 'Sensors', '$measure', u'$unit', '',
            [ #DEF
                ['value', 'value'],
            ],[ #vnames
                ['CDEF', 'valk', 'value,${multiplier},*',],
                ['VDEF', 'vmax', 'valk,MAXIMUM'],
                ['VDEF', 'vavg', 'valk,AVERAGE'],
                ['VDEF', 'vlast', 'valk,LAST'],
            ],[ #lines
                ['LINE', 'valk', '0000ff', 2, r'${measure}\l'],
                ['PRINT', 'vmax', r'$measure - Maximum: %.2lf %S${units}'],
                ['PRINT', 'vavg', r'Average: %.2lf %S${units}'],
                ['PRINT', 'vlast', r'Current: %.2lf %S${units}\l'],
            ]
        ],
    ] # end of graph types

