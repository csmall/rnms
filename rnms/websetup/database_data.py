# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011 Craig Small <csmall@enc.com.au>
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
        ['No Interface Type',0,0,'none','',1,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['TCP Ports',0,1,'tcp_ports','-sT -p1-500,600-1024',5,'LAST','103680',1,23,0,'tcp_ports',1,1,1,'',[
            ['Port Number','port',0,1,1,1,0,0,'',''],
            ['Check Content','check_content',0,1,0,1,0,0,'',''],
            ['Check Content URL','check_url',0,1,1,0,1,0,'',''],
            ['Check Content RegExp','check_regexp',0,1,0,1,0,0,'','']
            ], [
            [u'Established Connections', 'tcp_conn_number', 1,0,10000,0],
            [u'Connection Delay', 'conn_delay', 1,0,10000,0],
            ] ],
        ['Cisco System Info',1,1,'host_information','cisco,9.1,9.5',3,'AVERAGE','103680',300,9,0,'none',0,7,0,'ent.9',[
            ['Number of Processors','cpu_num',0,1,1,1,0,1,'',''],
            ['CPU Usage Threshold','cpu_threshold',0,1,0,1,0,60,'',''],
            ['System Name','name',1,1,1,1,0,1,'',''],
            ['Location','location',1,1,1,1,0,1,'',''],
            ['Contact','contact',1,1,1,1,0,1,'',''],
           ], [
            [u'CPU', 'cpu', 1,0,100,''],
            [u'Mem Used', 'mem_used', 1,0,100000000000,''],
            [u'Mem Free', 'mem_free', 1,0,100000000000,''],
            [u'Acct Packets', 'acct_packets', 3,0,100000000000,''],
            [u'Acct Bytes', 'acct_bytes', 1,0,100000000000,''],
            [u'TCP Active', 'tcp_active', 2,0,10000000,''],
            [u'TCP Passive', 'tcp_passive', 2,0,10000000,''],
            [u'TCP Established', 'tcp_established', 2,0,10000000,''],
               ] ],
        ['Physical Interfaces',1,1,'snmp_interfaces','',2,'AVERAGE','103680',300,3,1,'none',0,1,1,'.',[
            ['IP Address','address',1,1,1,1,0,'','',''],
            ['IP Mask','mask',0,1,1,1,0,'','',''],
            ['Peer Address','peer',0,1,1,1,0,'','',''],
            ['Input Bandwidth','bandwidthin',0,1,1,1,0,1,'',''],
            ['Output Bandwidth','bandwidthout',0,1,1,1,0,1,'',''],
            ['Percentile','percentile',0,1,0,1,0,'','',''],
            ['Flip In Out in Graphs','flipinout',0,1,1,1,0,0,'',''],
            ['Pings to Send','pings',0,1,1,1,0,50,'',''],
            ['Fixed Admin Status','fixed_admin_status',0,1,1,1,0,0,'','']
            ], [
            [u'Input Bytes', 'input', 2,0,0,'bandwidthin'],
            [u'Output Bytes', 'output', 2,0,0,'bandwidthout'],
            [u'Input Packets', 'inpackets', 2,0,0,'bandwidthin'],
            [u'Input Errors', 'inputerrors', 2,0,0,'bandwidthin'],
            [u'Output Errors', 'outputerrors', 2,0,0,'bandwidthout'],
            [u'Round Trip Time', 'rtt', 1,0,10000,''],
            [u'Packet Loss', 'packetloss', 1,0,1000,''],
            [u'Output Packets', 'outpackets', 2,0,0,'bandwidthout'],
            [u'Drops', 'drops', 2,0,0,'bandwidthout'],
                ] ],

        ['BGP Neighbors',1,1,'bgp_peers','',8,'AVERAGE','103680',300,90,0,'none',0,1,0,'.',[
            ['Local IP','local',1,1,1,0,1,'','',''],
            ['Remote IP','remote',0,1,1,0,0,'','',''],
            ['Autonomous System','asn',1,1,1,0,1,'','',''],
            ], [
            [u'BGP In Updates', 'bgpin', 2,0,10000000,''],
            [u'BGP Out Updates', 'bgpout', 2,0,10000000,''],
            [u'BGP Uptime', 'bgpuptime', 1,0,10000000,''],
            [u'Accepted Routes', 'accepted_routes', 1,0,9000000,''],
            [u'Advertised Routes', 'advertised_routes', 1,0,9000000,''],
                ] ],
        ['Storage',1,1,'storage','',9,'AVERAGE','103680',300,15,0,'none',0,9,0,'.',[
            ['Disk Type','storage_type',1,1,1,0,0,'','',''],
            ['Size (bytes)','size',1,1,1,1,0,'','',''],
            ['Usage Threshold','usage_threshold',0,1,0,1,0,80,'',''],
            ], [
            [u'Storage Block Size', 'storage_block_size', 1,0,0,'size'],
            [u'Storage Block Count', 'storage_block_count', 1,0,0,'size'],
            [u'Storage Used Blocks', 'storage_used_blocks', 1,0,0,'size'],
                ] ],
        ['CSS VIPs',0,1,'css_vips','',10,'AVERAGE','103680',300,17,0,'none',0,1,0,'ent.9',[
            [u'Owner','owner',1,1,1,0,1,'','',''],
            [u'VIP Address','address',1,1,1,0,1,'','',''],
            [u'Bandwidth','bandwidth',0,1,1,1,0,'','',''],
            ], [
            [u'Output', 'output', 2,0,0,'bandwidth'],
            [u'Hits', 'hits', 2,0,0,'bandwidth'],
                ] ],
        ['Solaris System Info',1,1,'host_information','solaris,sparc,sun,11.2.3.10,8072.3.2.3',12,'AVERAGE','103680',300,20,0,'none',0,1,0,'.',[
            [u'Number of Processes','cpu_num',0,1,1,0,1,'1','',''],
            [u'System Name','name',1,1,1,0,1,'','',''],
            [u'Location','location',1,1,1,0,1,'','',''],
            [u'Contact','contact',1,1,1,0,1,'','',''],
            ], [
            [u'CPU User Ticks', 'cpu_user_ticks', 2,0,86400,''],
            [u'CPU Idle Ticks', 'cpu_idle_ticks', 2,0,86400,''],
            [u'CPU Wait Ticks', 'cpu_wait_ticks', 2,0,86400,''],
            [u'CPU Kernel Ticks', 'cpu_kernel_ticks', 2,0,86400,''],
            [u'Swap Total', 'swap_total', 1,0,10000000000,''],
            [u'Swap Available', 'swap_available', 1,0,10000000000,''],
            [u'Mem Total', 'mem_total', 1,0,10000000000,''],
            [u'Mem Available', 'mem_available', 1,0,10000000000,''],
            [u'Load Average 1', 'load_average_1', 1,0,1000,''],
            [u'Load Average 5', 'load_average_5', 1,0,1000,''],
            [u'Load Average 15', 'load_average_15', 1,0,1000,''],
                ] ],
        ['Linux/Unix System Info',1,1,'host_information','2021.250.10,linux,2021.250.255,freebsd,netSnmp,8072',11,'AVERAGE','103680',300,21,0,'none',0,10,0,'.',[
            [u'Number of Processes','cpu_num',0,1,1,0,1,'1','',''],
            [u'CPU Usage Threshold','cpu_threshold',0,0,1,0,1,'80','',''],
            [u'System Name','name',1,1,1,0,1,'','',''],
            [u'Location','location',1,1,1,0,1,'','',''],
            [u'Contact','contact',1,1,1,0,1,'','',''],
            ], [
            [u'CPU User Ticks', 'cpu_user_ticks', 2,0,86400,''],
            [u'CPU Idle Ticks', 'cpu_idle_ticks', 2,0,86400,''],
            [u'CPU Nice Ticks', 'cpu_nice_ticks', 2,0,86400,''],
            [u'CPU System Ticks', 'cpu_system_ticks', 2,0,86400,''],
            [u'Load Average 1', 'load_average_1', 1,0,1000,''],
            [u'Load Average 5', 'load_average_5', 1,0,1000,''],
            [u'Load Average 15', 'load_average_15', 1,0,1000,''],
            [u'Num Users', 'num_users', 1,0,10000,''],
            [u'Num Procs', 'num_procs', 1,0,10000,''],
            [u'TCP Active', 'tcp_active', 2,0,10000,''],
            [u'TCP Passive', 'tcp_passive', 2,0,10000,''],
            [u'TCP Established', 'tcp_established', 2,0,10000,''],
                ] ],
        ['Windows System Info',1,1,'host_information','enterprises.311',13,'AVERAGE','103680',300,28,0,'none',0,11,0,'.',[
            [u'Number of Processes','cpu_num',0,1,1,0,1,'1','',''],
            [u'CPU Usage Threshold','cpu_threshold',0,0,1,0,1,'80','',''],
            [u'System Name','name',1,1,1,0,1,'','',''],
            [u'Location','location',1,1,1,0,1,'','',''],
            [u'Contact','contact',1,1,1,0,1,'','',''],
            ], [
            [u'CPU', 'cpu', 1,0,100,''],
            [u'Num Users', 'num_users', 1,0,10000,''],
            [u'Num Procs', 'num_procs', 1,0,10000,''],
            [u'TCP Active', 'tcp_active', 2,0,10000,''],
            [u'TCP Passive', 'tcp_passive', 2,0,10000,''],
            [u'TCP Established', 'tcp_established', 2,0,10000,''],
                ] ],
        ['Cisco MAC Accounting',1,1,'cisco_accounting','',14,'AVERAGE','103680',300,33,0,'none',0,1,0,'.',[
            [u'IP Address','address',1,1,1,0,1,'','',''],
            [u'MAC Address','mac',0,1,1,0,1,'','',''],
            ], [
            [u'Input', 'input', 2,0,100000000,''],
            [u'Output', 'output', 2,0,100000000,''],
            [u'Input Packets', 'inputpackets', 2,0,100000000,''],
            [u'Output Packets', 'outputpackets', 2,0,100000000,''],
                ] ],
        ['Smokeping Host',1,1,'smokeping','/var/lib/smokeping',15,'AVERAGE','103680',300,34,0,'none',0,8,0,'',[
            ], [
            [u'RTT', 'tcp_active', 2,0,10000,''],
            [u'Packet Loss', 'packetloss', 2,0,1000,''],
                ] ],
        ['Applications',1,0,'hostmib_apps','',16,'AVERAGE','103680',300,44,0,'none',0,1,0,'.',[
            [u'Instances at Discovery','instances',1,1,1,0,1,'','',''],
            [u'Ignore Case','ignore_case',1,1,1,0,1,'','',''],
            ], [
            [u'Current Instances', 'current_instances', 1,0,99999,''],
            [u'Used Memory', 'used_memory', 1,0,9999999,''],
                ] ],
        ['Cisco Power Supply',1,1,'cisco_envmib','PowerSupply,5.1.2,5.1.3',17,'','103680',300,1,1,'none',0,1,0,'ent.9',[
            ], [
                ] ],
        ['Cisco Temperature',1,1,'cisco_envmib','Temperature,3.1.2,3.1.6',18,'AVERAGE','103680',300,37,1,'none',0,1,0,'ent.9',[
            ], [
            [u'Temperature', 'temperature', 1,0,100,''],
                ] ],
        ['Cisco Voltage',1,1,'cisco_envmib','Voltage,2.1.2,2.1.7',19,'','103680',300,1,1,'none',0,1,0,'ent.9',[ ], [ ] ],
        ['Cisco SA Agent',1,1,'cisco_saagent','',20,'AVERAGE','103680',300,39,0,'none',0,1,0,'ent.9',[
            ], [
            [u'Forward Jitter', 'forward_jitter', 1,0,100,''],
            [u'Backward Jitter', 'backward_jitter', 1,0,100,''],
            [u'RT Latency', 'rt_latency', 1,0,100,''],
            [u'Forward Packetloss', 'forward_packetloss', 1,0,100,''],
            [u'Backward Packetloss', 'backward_packetloss', 1,0,100,''],
                ] ],
        ['Reachable',1,1,'reachability','',21,'AVERAGE','103680',300,41,0,'none',0,1,0,'',[
            [u'Pings to Send','pings',0,1,0,1,0,'','',''],
            [u'Loss Threshold%','threshold',0,1,0,1,0,'','',''],
            [u'Interval (ms)','interval',0,1,0,1,0,'','',''],
            ], [
            [u'RTT', 'rtt', 1,0,10000,''],
            [u'Packetloss', 'packetloss', 1,0,1000,''],
                ] ],
        ['Linux Traffic Control',1,1,'linux_tc','.1.3.6.1.4.1.2021.5001',22,'AVERAGE','103680',300,43,1,'none',0,1,0,'.',[
            [u'Rate','rate',0,1,0,0,1,'','',''],
            [u'Ceiling','ceil',0,1,0,0,1,'','',''],
            ], [
            [u'Bytes', 'bytes', 2,0,0,'ceil'],
            [u'Packets', 'packets', 2,0,0,'ceil'],
                ] ],
        ['NTP',0,1,'ntp_client','',23,'AVERAGE','103680',300,1,0,'none',0,1,0,'',[], [] ],
        ['UDP Ports',0,0,'tcp_ports','-sU -p1-500,600-1024 --host_timeout 15000',24,'AVERAGE','103680',300,45,0,'tcp_ports',1,1,0,'',[
            ], [
            [u'Connection Delay', 'conn_delay', 1,0,10000,''],
                ] ],
        ['Compaq Physical Drives',0,1,'cpqmib','phydrv',25,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[
            [u'Controller', 'controller', 1,1,0, 0,1, '','',''],
            [u'Drive', 'drvindex', 1,1,0, 0,1, '','',''],
            [u'Drive Model', 'drive', 0,1,0, 0,1, '','',''],
            ], [
                ] ],
        ['Compaq Fans',0,1,'cpqmib','fans',26,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[
            [u'Location', 'location', 1,1,1, 0,1, '','',''],
            [u'Chassis', 'chassis', 0,1,1, 0,1, '','',''],
            [u'Fan', 'fan_index', 0,1,1, 0,1, '','',''],
            ], [
                ] ],
        ['Compaq Temperature',0,1,'cpqmib','temperature',27,'AVERAGE','103680',300,46,0,'none',0,1,0,'.',[
            [u'Location', 'location', 0,1,1, 0,1, '','',''],
            [u'Chassis', 'chassis', 0,1,1, 0,1, '','',''],
            [u'Sensor', 'temp_index', 0,1,1, 0,1, '','',''],
            ], [
            [u'Temperature', 'temperature', 1,0,1000,''],
                ] ],
        ['IIS Webserver Information',0,1,'iis_info','',28,'AVERAGE','103680',300,50,0,'none',0,1,0,'.',[
            ], [
            [u'Total Bytes Received', 'tbr', 2,0,100000000,''],
            [u'Total CGI Requests', 'tcgir', 2,0,100000000,''],
            [u'Total Files Sent', 'tfs', 2,0,100000000,''],
            [u'Total Gets', 'tg', 2,0,100000000,''],
            [u'Total Posts', 'tp', 2,0,100000000,''],
                ] ],
        ['Apache',0,1,'apache','',30,'AVERAGE','103680',300,53,0,'none',1,1,0,'',[
            ], [
            [u'Total Accesses', 'tac', 2,0,100000000,''],
            [u'Total kBytes', 'tkb', 2,0,100000000,''],
            [u'CPU Load', 'cplo', 1,0,1000,''],
            [u'Uptime', 'up', 1,0,10000000,''],
            [u'Bytes Per Request', 'bpr', 1,0,10000000,''],
            [u'Busy Workers', 'bw', 1,0,1000,''],
            [u'Idle Workers', 'iw', 1,0,1000,''],
                ] ],
        ['APC',1,1,'apc','enterprises.318',31,'AVERAGE','103680',300,61,0,'none',0,1,0,'.',[
            ], [
            [u'Battery Capacity', 'capacity', 1,0,100,''],
            [u'Output Load', 'load', 1,0,100,''],
            [u'Input Voltage', 'in_voltage', 1,0,400,''],
            [u'Output Voltage', 'out_voltage', 1,0,400,''],
            [u'Time Remaining', 'time_remaining', 1,0,100000000,''],
            [u'Temperature', 'temperature', 1,0,200,''],
                ] ],
        ['Alteon Real Server',1,1,'alteon_realservers','',33,'AVERAGE','103680',300,66,0,'none',0,1,0,'ent.1872',[
            [u'Hostname', 'hostname', 1,1,1, 1,0, '','',''],
            [u'Max Connections', 'max_connections', 0,1,1, 1,0, '','',''],
            ], [
            [u'Total Sessions', 'total_sessions', 2,0,100000000,''],
            [u'Current Sessions', 'current_sessions', 1,0,0,'max_connections'],
            [u'Failures', 'failures', 2,0,10000,''],
            [u'Octets', 'octets', 2,0,100000000,''],
                ] ],
        ['Alteon Virtual Server',0,1,'alteon_virtualservers','',34,'AVERAGE','103680',300,70,0,'none',0,1,0,'ent.1872',[
            [u'Hostname', 'hostname', 1,1,1, 1,0, '','',''],
            ], [
            [u'Total Sessions', 'total_sessions', 2,0,100000000,''],
            [u'Current Sessions', 'current_sessions', 1,0,20000,''],
            [u'Octets', 'octets', 2,0,100000000,''],
                ] ],
        ['Alteon Real Services',0,1,'alteon_realservices','',35,'AVERAGE','103680',300,73,0,'none',0,1,0,'ent.1872',[
            [u'Hostname', 'hostname', 1,1,1, 1,0, '','',''],
            [u'Address', 'address', 1,1,1, 1,0, '','',''],
            [u'Port', 'port', 1,1,1, 1,0, '','',''],
            [u'Real Server', 'real_server', 0,0,1, 0,1, '','',''],
            ], [
            [u'Response Time', 'response_time', 1,0,10000,''],
                ] ],
        ['Alteon System Info',1,1,'host_information','enterprises.1872',36,'AVERAGE','103680',300,75,0,'none',0,1,0,'ent.1872',[
            [u'System Name','name',1,1,1,0,1,'','',''],
            [u'Location','location',1,1,1,0,1,'','',''],
            [u'Contact','contact',1,1,1,0,1,'','',''],
            [u'Number of CPUs','cpu_num',0,0,1, 0,0, '','',''],
            ], [
            [u'TCP Active', 'tcp_active', 2,0,10000,''],
            [u'TCP Passive', 'tcp_passive', 2,0,10000,''],
            [u'TCP Established', 'tcp_established', 2,0,10000,''],
            [u'Memory Total', 'mem_total', 1,0,10000000000,''],
            [u'Memory Used', 'mem_used', 1,0,10000000000,''],
            [u'CPU A 1 sec', 'cpua_1sec', 1,0,1000,''],
            [u'CPU A 4 sec', 'cpua_4sec', 1,0,1000,''],
            [u'CPU A 64 sec', 'cpua_64sec', 1,0,1000,''],
            [u'CPU B 1 sec', 'cpub_1sec', 1,0,1000,''],
            [u'CPU B 4 sec', 'cpub_4sec', 1,0,1000,''],
            [u'CPU B 64 sec', 'cpub_64sec', 1,0,1000,''],
                ] ],
        ['Brocade Sensors',0,0,'brocade_sensors','',37,'AVERAGE','103680',300,77,0,'none',0,1,0,'ent.1588',[
            [u'Type','sensor_type',0,1,1, 0,0,'','',''],
            ], [
            [u'Sensor Value', 'sensor_value', 1,0,30000000,''],
                ] ],
        ['Brocade FC Ports',0,0,'brocade_fcports','',38,'AVERAGE','103680',300,78,0,'none',0,1,0,'ent.1588',[
            [u'Physical Status','phy',0,1,1, 0,0,'','',''],
            ], [
            [u'Tx Words', 'tx_words', 2,0,100000000,''],
            [u'Rx Words', 'rx_words', 2,0,100000000,''],
            [u'Tx Frames', 'rx_frames', 2,0,100000000,''],
            [u'Rx Words', 'rx_frames', 2,0,100000000,''],
                ] ],
        ['Windows Logical Disks',1,1,'informant_ldisks','',40,'AVERAGE','103680',300,82,0,'none',0,1,0,'.',[
            ], [
            [u'lDisk % Read Time', 'inf_d_read_time', 1,0,100,''],
            [u'lDisk % Write Time', 'inf_d_write_time', 1,0,100,''],
            [u'lDisk Read Rate', 'inf_d_read_rate', 1,0,1048576000,''],
            [u'lDisk Write Rate', 'inf_d_write_rate', 1,0,1048576000,''],
                ] ],
        ['UPS',1,1,'ups','',41,'AVERAGE','103680',300,84,0,'none',0,1,0,'.',[
            [u'Identification','ident',0,1,1, 0,1,'','',''],
            [u'UPS Type','ups_type',0,1,1, 0,1,'','',''],
            ], [
            [u'Battery Temperature', 'temperature', 1,0,200,''],
            [u'Minutes Remaining', 'minutes_remaining', 1,0,10000200,''],
            [u'Charge Remaining', 'charge_remaining', 1,0,10000200,''],
                ] ],
        ['UPS Lines',0,1,'ups_lines','',42,'AVERAGE','103680',300,85,0,'none',0,1,0,'.',[], [] ],
        ['IPTables Chains',1,1,'linux_iptables','.1.3.6.1.4.1.2021.5002',43,'AVERAGE','103680',300,89,1,'none',0,1,0,'.',[], [] ],
        ['Cisco PIX',1,1,'pix_connections','',44,'AVERAGE','103680',300,91,0,'none',0,1,0,'ent.9',[], [] ],
        ['Cisco NAT',0,1,'simple','.1.3.6.1.4.1.9.10.77.1.2.1.0,NAT',45,'AVERAGE','103680',300,93,0,'none',0,1,0,'ent.9',[], [] ],
        ['Sensors',1,1,'sensors','',46,'AVERAGE','103680',300,94,1,'none',0,1,0,'.',[], [] ],
        ['OS/400 System Info',1,1,'simple','.1.3.6.1.4.1.2.6.4.5.1.0,OS400',47,'AVERAGE','103680',300,95,0,'none',0,1,0,'.',[], [] ],
        ['Dell Chassis',1,1,'simple','.1.3.6.1.4.1.674.10892.1.200.10.1.2.1,Chassis status',48,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['PDU',1,1,'pdu','',49,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['PDU Banks',0,1,'pdu_banks','',50,'AVERAGE','103680',300,99,0,'none',0,1,0,'.',[], [] ],
        ['IBM Component Health',1,0,'ibm_ComponentHealth','',57,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['IBM Blade server',1,0,'ibm_blade_servers','',51,'AVERAGE','103680',300,106,0,'none',0,1,0,'.',[], [] ],
        ['Generic FC Ports',1,0,'fc_ports','',52,'AVERAGE','103680',300,105,0,'none',0,1,0,'.',[], [] ],
        ['Cisco Wireless Device',1,0,'simple','.1.3.6.1.4.1.9.9.273.1.1.2.1.1.1,Cisco AP',53,'AVERAGE','103680',300,101,0,'none',0,1,0,'ent.9',[], [] ],
        ['IBM Blade Power',1,0,'ibm_blade_power','',54,'AVERAGE','103680',300,107,0,'none',0,1,0,'.',[], [] ],
        ['Compaq Power Supply',1,0,'cpqmib','powersupply',55,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['IBM Storage Controller',0,0,'ibm_ds_storage','storagesubsystem',56,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['Informant Disks 64',1,1,'informant_adv_ldisks','',58,'AVERAGE','103680',300,102,0,'none',0,1,0,'.',[], [] ]
        ]
    
config_transfers = [
    [u'No Configuration Transfer','none'],
    [u'Cisco IOS, Newer than 12.0 (CONFIG-COPY-MIB)','cisco_cc'],
    [u'Cisco IOS, Older than 12.0 (SYS-MIB)','cisco_sys'],
    [u'Cisco CatOS, Catalyst Switches (STACK-MIB)','cisco_catos']
    ]

event_types = [
    [u'Unknown', u'Warning', u'<interface> <user> <state> <info>',0,1,0,1,1],
    [u'Configuration', u'Warning', u'<user>: Changed Configuration from <info> <interface>',0,1,0,1,1],
    [u'Interface Protocol', u'Fault', u'Interface <attribute> Protocol <state> <info> (<client> <interface-description>)',1,1,0,1,1],
    [u'Interface Link', u'Big Fault', u'Interface <attribute> Link <state> <info> (<client> <interface-description>)',0,1,0,1,1],
    [u'Controller Status', u'Big Fault', u'Controller  <info> <attribute> <state>',0,1,0,1,1],
    [u'BGP Status', u'Critical', u'BGP Neighbor <attribute> <state> <info> (<client> <interface-description>)',1,1,0,1,1],
    [u'Interface Shutdown', u'Big Fault', u'Interface <attribute> <info> <state> (<client> <interface-description>)',0,4,0,1,1],
    [u'Command', u'Warning', u'<user>: <info>',0,1,0,1,1],
    [u'RShell Attempt', u'Information', u'RShell attempt from <info> <state>',0,1,0,1,1],
    [u'SLA', u'Information', u'<attribute> <info> (<client> <interface-description>)',1,1,1800,1,1],
    [u'Clear Counters', u'Information', u'<user> Cleared Counters of <attribute>  (<client> <interface-description>)',0,1,0,1,1],
    [u'TCP/UDP Service', u'Service', u'TCP/UDP Service <attribute> <state> (<client> <interface-description>) <info>',1,1,0,1,1],
    [u'Administrative', u'Administrative', u'<attribute> <info>',1,1,1800,1,1],
    [u'Environmental', u'Critical', u'<attribute> <state> <info>',1,1,0,1,1],
    [u'PIX Event', u'Information', u'<info>',0,1,0,1,1],
    [u'PIX Port', u'Warning', u'<state> <info> packet from <user> to <attribute>',0,1,0,1,1],
    [u'Duplex Mismatch', u'Warning', u'Duplex Mismatch, <attribute> is not full duplex and <user> <info> is full duplex',0,1,0,1,1],
    [u'ACL', u'Information', u'ACL <attribute> <state> <info> packets from <user>',0,1,0,1,1],
    [u'BGP Notification', u'Information', u'Notification <state> <attribute> <info>',0,1,0,1,1],
    [u'Excess Collitions', u'Warning', u'Excess Collitions on Interface <attribute>',0,1,0,1,1],
    [u'Application', u'Critical', u'Application <attribute> is <state> <info> (<client> <interface-description>)',1,1,0,1,1],
    [u'TCP Content', u'Service', u'Content Response on <attribute> is <state> (<client> <interface-description>) <info>',1,1,0,1,1],
    [u'Reachability', u'Critical', u'Host is <state> with <info>',1,1,0,1,1],
    [u'NTP', u'Information', u'<attribute> is <state> <info>',1,1,0,1,1],
    [u'Tool Action', u'Critical', u'<attribute> <info> changed to <state> by <user> (<client> <interface-description>)',0,1,0,1,1],
    [u'Internal', u'Information', u'<user> <attribute> <state> <info>',0,1,0,1,0],
    [u'Syslog', u'Information', u'<attribute>: <info>',0,1,0,1,1],
    [u'Hide this Event', u'Information', u'<attribute> <user> <state> <info>',0,1,0,0,1],
    [u'Win Info', u'Information', u'<attribute>: <info> (ID:<state>)',0,1,0,2,1],
    [u'Win Warning', u'Warning', u'<attribute>: <info> (ID:<state>)',0,1,0,1,1],
    [u'Win Error', u'Fault', u'<attribute>: <info> (ID:<state>)',0,1,0,1,1],
    [u'Win Security', u'Fault', u'<info> (ID:<state>)',0,1,0,1,1],
    [u'SQL', u'Fault', u'SQL <attribute> is <state> <info>',1,1,0,1,1],
    [u'APC Status', u'Critical', u'<attribute> is <state> <info>',1,1,0,1,1],
    [u'PIX Debug', u'Administrative', u'<info> (ID:<attribute>)',0,1,0,2,1],
    [u'PIX Info', u'Information', u'<info> (ID:<attribute>)',0,1,0,2,1],
    [u'PIX Notif', u'Warning', u'<info> (ID:<attribute>)',0,1,0,2,1],
    [u'PIX Warn', u'Service', u'<info> (ID:<attribute>)',0,1,0,2,1],
    [u'PIX Error', u'Fault', u'<info> (ID:<attribute>)',0,1,0,2,1],
    [u'PIX Crit', u'Big Fault', u'<info> (ID:<attribute>)',1,1,0,1,1],
    [u'PIX Alert', u'Critical', u'<info> (ID:<attribute>)',1,1,0,1,1],
    [u'Alteon RServer', u'Fault', u'Real Server <attribute> is <state>',1,1,0,1,1],
    [u'Alteon Service', u'Fault', u'Real Service <attribute> is <state> <info>',1,1,0,1,1],
    [u'Alteon VServer', u'Fault', u'Virtual Server <attribute> is <state> <info>',0,1,0,1,1],
    [u'Brocade FC Port', u'Fault', u'<attribute> <state> (<info>)',1,1,0,1,1],
    [u'ISDN', u'Information', u'<attribute> <state> <info>',1,1,0,1,1],
    [u'To delete', u'Administrative', u'<info>  <state>  <attribute> <user>',0,1,0,2,1],
    [u'IBM error', u'Critical', u'<info> (id:<attribute>)',1,1,0,1,1],
    [u'IBM Warning',127,u'<attribute> is in <state> state',1,1,0,1,1],
    [u'Disable polling', u'Administrative', u'Polling for host <attribute> is disabled (enabling time: <info>)',0,1,0,1,0],
    [u'IBM San Trap', u'Critical', u'<user>: <state> <info> (<attribute>)',1,1,0,1,1],
    [u'OS/400 Error', u'Critical', u'A subsystem is <state> on the OS/400',1,1,0,1,1],
    [u'Enable polling', u'Administrative', u'Polling for host <attribute> is enabled',0,1,0,1,0],
    [u'Storage Controller', u'Big Fault', u'<info>',1,1,0,1,1]
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
            True,None,1,2,6,[]],
        [u'%BGP-3-NOTIFICATION: (\S+ \S+) neighbor (\S+) \S+ (\S+ \S+ \S+) \S+ \S+',
            True,None,2,1,36,[['info',3]]],
        [u'%CDP-4-DUPLEX_MISMATCH: duplex mismatch discovered on (\S+)',
            True,None,1,None,34,[]],
        [u'%CLEAR-5-COUNTERS: Clear counter on \S+ (\S+) by (\S+)',
            True,None,1,None,17,[['user',2,]]],

        [u'%CONTROLLER-5-UPDOWN: Controller \S+ (\S+), changed state to (\S+) \([^)]+\)$',
            True,None,1,2,5,[['info',3]]],
        [u'%ISDN-6-CONNECT: Interface (\S+) is now (\S+) (.+)$',
            True,None,1,2,72,[['info',3]]],
        [u'%LINK-3-UPDOWN: Interface (\S+), changed state to (\S+)',
            True,None,1,2,4,[]],
        [u'%LINK-5-CHANGED: Interface (\S+) changed state to (\S+)',
            True,None,1,2,7,[]],
        [u'%LINEPROTO-5-UPDOWN: Line protocol on Interface (\S+), changed to (\S+)',
            False,None,1,2,3,[]],
        [u'%SYS-5-CONFIG-(?:_I|): Configured from (\S+) by (\S+)$',
            True,None,None,None,2,[['source',1],['proto',2]]],

        [u'%SYS-5-(?:RESTART|RELOAD): (.+)$',
            True,None,None,None,26,[['info',1]]],
        [u'%SEC-6-IPACCESSLOG(?:DP|P|NP|S): list (.+)$',
            True,None,None,None,35,[['info',1]]],
        [u'EXCESSCOLL: (\S+)',
            False,None,1,None,37,[]],
        [u'WebOS <slb>: No services are available for Virtual Server\d+:(\S+)',
            True,None,1,'down',70,[]],
        [u'%ISDN-6-DISCONNECT: Interface (\S+) (\S+) (.+)$',
            True,None,1,2,72,[['info',3]]],
        [u'%PIX-4-106023: (.+)$',
            True,None,None,None,29,[['info',1]]],
        [u'UPS: ([^.]+)\. (.+)$',
            True,None,'UPS',None,26,[['info',1]]],
        [u'WebOS <slb>: real server (\S+) operational',
            True,None,1,'up',68,[]],
        [u'WebOS <slb>: cannot contact real server (\S+)',
            True,None,1,'down',68,[]],
        [u'WebOS <slb>: Services are available for Virtual Server\d+:(\S+)',
            True,None,1,'up',70,[]],
        [u'WebOS <slb>: real service (\S+) operational',
            True,None,1,'up',69,[]],
        [u'WebOS <slb>: cannot contact real service (\S+)',
            True,None,1,'down',69,[]],
        [u'%RCMD-4-RSHPORTATTEMPT: Attempted to connect to RSHELL from (\S+)',
            True,None,None,None,9,[['source',1]]],

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
        [u'Smokeping Host',3, u'Smokeping:',12,100,14, [
            [23,1],
            [2,1],
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
        [u'Round Trip Time > 60ms', '<rtt>', '>', 60, u'RTT > 60', u'<rtt>', u',s'],
        [u'Packet Loss > 20%', '<packetloss> * 100 / <pings>', '>', 20, u'PL > 20%', u'<packetloss> * 100 / <pings>', u'%'],
        [u'Input Traffic < 95%', '<in> * 100 / <bandwidthin>', '<', 95, u'IN < 95%', u'<in> / 1000', u'kbps'],
        [u'AND', 'AND','=',0,u'', u'', u''],
        [u'OR', 'OR','=',0,u'', u'', u''],
        [u'Round Trip Time > 700ms', '<rtt>', '>', 700, u'RTT > 700', u'<rtt>', u'ms'],
        [u'Round Trip Time > 900ms', '<rtt>', '>', 900, u'RTT > 900', u'<rtt>', u'ms'],
        [u'Packet Loss > 50%', '<packetloss> * 100 / <pings>', '>', 50, u'PL > 50%', u'<packetloss> * 100 / <pings>', u'%'],
        # id 10 is missing
        [u'Input Traffic > 90%', '<in> * 100 / <bandwidthin>', '>', 90, u'IN > 90%', u'<in> / 1000', u'kbps'],
        [u'Input Traffic < 1%', '<in> * 100 / <bandwidthin>', '<', 1, u'IN < 1%', u'<in> / 1000', u'kbps'],
        [u'Output Traffic > 90%', '<out> * 100 / <bandwidthout>', '>', 90, u'IN > 90%', u'<out> / 1000', u'kbps'],
        [u'Output Traffic < 95%', '<out> * 100 / <bandwidthout>', '<', 95, u'IN < 95%', u'<out> / 1000', u'kbps'],
        [u'Input Error Rate > 20%', '(<inerrors> * 100) / (<inpackets> + 1 )', '>', 20, u'IN ERR > 20%', u'(<inerrors> * 100) / (<inpackets> + 1)', u'% = <inerrors> Eps'],
        [u'Input Error Rate > 10%', '(<inerrors> * 100) / (<inpackets> + 1 )', '>', 10, u'IN ERR > 10%', u'(<inerrors> * 100) / (<inpackets> + 1)', u'% = <inerrors> Eps'],
        #17 is missing
        [u'Drops > %1', '(<drops> * 100) / (<outpackets> + 1)', '>', 1, u'Drops > 1%', u'(<drops> * 100) / (<outpackets> + <drops> + 1)', u'% = <drops> dps'],
        [u'Drops > %2', '(<drops> * 100) / (<outpackets> + 1)', '>', 2, u'Drops > 2%', u'(<drops> * 100) / (<outpackets> + <drops> + 1)', u'% = <drops> dps'],
        [u'Packet Loss > 10%', '<packetloss> * 100 / <pings>', '>', 10, u'PL > 10%', u'<packetloss> * 100 / <pings>', u'%'],
        [u'Drops > %10', '(<drops> * 100) / (<outpackets> + 1)', '>', 10, u'Drops > 10%', u'(<drops> * 100) / (<outpackets> + <drops> + 1)', u'% = <drops> dps'],
        [u'Input Traffic < 99%', '<in> * 100 / <bandwidthin>', '<', 99, u'IN < 99%', u'<in> / 1000', u'kbps'],
        [u'Output Traffic < 99%', '<out> * 100 / <bandwidthout>', '<', 99, u'IN < 99%', u'<out> / 1000', u'kbps'],
        [u'High CPU Utilization', '<cpu> - <cpu_threshold>', '>', 0, u'Usage > <cpu_threshold>', u'<cpu>', u'%'],
        [u'Packet Loss > 10% SP', '<packetloss>', '>', 10, u'PL > 10%', u'<packetloss>', u'%'],
        [u'Used Storage', '(<storage_used_blocks> * 100) / <storage_block_count> - <usage_threshold>', '>', 0, u'Used > <usage_threshold>', u'(<storage_used_blocks> * 100) / <storage_block_count>', u'%'],
        [u'Load Average > 5', '<load_average_5>', '>', 5, u'Load Average > 5', u'<load_average_5>', u''],
        [u'High CPU Util (ticks)', '(<cpu_user_ticks> + <cpu_nice_ticks> + <cpu_system_ticks>) * 100 / (<cpu_user_ticks> + <cpu_idle_ticks> + <cpu_nice_ticks> + <cpu_system_ticks>) - <cpu_threshold>', '>', 0, u'Usage > <cpu_threshold>%', u'(<cpu_user_ticks> + <cpu_nice_ticks> + <cpu_system_ticks>) * 100 / (<cpu_user_ticks> + <cpu_idle_ticks> + <cpu_nice_ticks> + <cpu_system_ticks>)', u'%'],
        [u'Memory Usage > 80%', '<mem_used> * 100 / (<mem_used> + <mem_free>)', '>', 80, 'Memory Usage > 80%', u'<mem_used> * 100 / (<mem_used> + <mem_free>)', u'%'],
        [u'CPU Utilization > 90%', '<cpu>', '>', 90, u'CPU > 90%', u'<cpu>', u'%'],
        [u'Too Many Processes', '<num_procs> - <proc_threshold>', '>', 0, u'Processes > <proc_threshold>', u'<num_procs>', u'Processes'],
        [u'APC temp > 55', '<temperature> - 55', '>', 0, u'APC temp > 55', u'<temperature', u'C'],
        [u'APC time < 50 minutes', '<time_remaining>', '<', 30000, u'APC time < 50 minutes', u'<time_remaining> / 6000', u'mins'
        ],
        ]

