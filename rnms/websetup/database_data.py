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
attribute_types = [
        ['No Interface Type',0,0,'none','',1,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['TCP Ports',0,1,'tcp_ports','-sT -p1-500,600-1024',5,'LAST','103680',1,23,0,'tcp_ports',1,1,1,'',[
            ['Port Description','description',1,1,1,1,1,1,0,'',''],
            ['Port Number','port',2,0,1,1,1,0,0,'',''],
            ['Check Content','check_content',3,0,1,0,1,0,0,'',''],
            ['Check Content URL','check_url',4,0,1,1,0,1,0,'',''],
            ['Check Content RegExp','check_regexp',5,0,1,0,1,0,0,'','']
            ], [] ],
        ['Cisco System Info',1,1,'host_information','cisco,9.1,9.5',3,'AVERAGE','103680',300,9,0,'none',0,7,0,'ent.9',[
            ['Description','description',1,1,1,1,1,0,1,'',''],
            ['Number of Processors','cpu_num',2,0,1,1,1,0,1,'',''],
            ['CPU Usage Threshold','cpu_threshold',3,0,1,0,1,0,60,'',''],
            ['System Name','name',4,1,1,1,1,0,1,'',''],
            ['Location','location',5,1,1,1,1,0,1,'',''],
            ['Contact','contact',5,1,1,1,1,0,1,'',''],
           ], [] ],
        ['Physical Interfaces',1,1,'snmp_interfaces','',2,'AVERAGE','103680',300,3,1,'none',0,1,1,'.',[
            ['Description','description',1,1,1,1,1,0,'','',''],
            ['IP Address','address',1,1,1,1,1,0,'','',''],
            ['IP Mask','mask',1,0,1,1,1,0,'','',''],
            ['Peer Address','peer',2,0,1,1,1,0,'','',''],
            ['Input Bandwidth','bandwidthin',3,0,1,1,1,0,1,'',''],
            ['Output Bandwidth','bandwidthout',4,0,1,1,1,0,1,'',''],
            ['Percentile','percentile',5,0,1,0,1,0,'','',''],
            ['Flip In Out in Graphs','flipinout',6,0,1,1,1,0,0,'',''],
            ['Pings to Send','pings',7,0,1,1,1,0,50,'',''],
            ['Fixed Admin Status','fixed_admin_status',8,0,1,1,1,0,0,'','']
            ], [] ],

        ['BGP Neighbors',1,1,'bgp_peers','',8,'AVERAGE','103680',300,90,0,'none',0,1,0,'.',[
            ['Local IP','local',1,1,1,1,0,1,'','',''],
            ['Remote IP','remote',2,0,1,1,0,0,'','',''],
            ['Autonomous System','asn',3,1,1,1,0,1,'','',''],
            ['Description','asn',4,1,1,0,0,0,'','',''],
            ], [] ],
        ['Storage',1,1,'storage','',9,'AVERAGE','103680',300,15,0,'none',0,9,0,'.',[
            ['Disk Type','storage_type',1,1,1,1,0,0,'','',''],
            ['Size (bytes)','size',2,1,1,1,1,0,'','',''],
            ['Description','description',3,1,1,1,1,0,'','',''],
            ['Usage Threshold','usage_threshold',4,0,1,0,1,0,80,'',''],
            ], [] ],
        ['CSS VIPs',0,1,'css_vips','',10,'AVERAGE','103680',300,17,0,'none',0,1,0,'ent.9',[], [] ],
        ['Solaris System Info',1,1,'host_information','solaris,sparc,sun,11.2.3.10,8072.3.2.3',12,'AVERAGE','103680',300,20,0,'none',0,1,0,'.',[], [] ],
        ['Linux/Unix System Info',1,1,'host_information','2021.250.10,linux,2021.250.255,freebsd,netSnmp,8072',11,'AVERAGE','103680',300,21,0,'none',0,10,0,'.',[], [] ],
        ['Windows System Info',1,1,'host_information','enterprises.311',13,'AVERAGE','103680',300,28,0,'none',0,11,0,'.',[], [] ],
        ['Cisco MAC Accounting',1,1,'cisco_accounting','',14,'AVERAGE','103680',300,33,0,'none',0,1,0,'.',[], [] ],
        ['Smokeping Host',1,1,'smokeping','/var/lib/smokeping',15,'AVERAGE','103680',300,34,0,'none',0,8,0,'',[], [] ],
        ['Applications',1,0,'hostmib_apps','',16,'AVERAGE','103680',300,44,0,'none',0,1,0,'.',[], [] ],
        ['Cisco Power Supply',1,1,'cisco_envmib','PowerSupply,5.1.2,5.1.3',17,'','103680',300,1,1,'none',0,1,0,'ent.9',[], [] ],
        ['Cisco Temperature',1,1,'cisco_envmib','Temperature,3.1.2,3.1.6',18,'AVERAGE','103680',300,37,1,'none',0,1,0,'ent.9',[], [] ],
        ['Cisco Voltage',1,1,'cisco_envmib','Voltage,2.1.2,2.1.7',19,'','103680',300,1,1,'none',0,1,0,'ent.9',[], [] ],
        ['Cisco SA Agent',1,1,'cisco_saagent','',20,'AVERAGE','103680',300,39,0,'none',0,1,0,'ent.9',[], [] ],
        ['Reachable',1,1,'reachability','',21,'AVERAGE','103680',300,41,0,'none',0,1,0,'',[], [] ],
        ['Linux Traffic Control',1,1,'linux_tc','.1.3.6.1.4.1.2021.5001',22,'AVERAGE','103680',300,43,1,'none',0,1,0,'.',[], [] ],
        ['NTP',0,1,'ntp_client','',23,'AVERAGE','103680',300,1,0,'none',0,1,0,'',[], [] ],
        ['UDP Ports',0,0,'tcp_ports','-sU -p1-500,600-1024 --host_timeout 15000',24,'AVERAGE','103680',300,45,0,'tcp_ports',1,1,0,'',[], [] ],
        ['Compaq Physical Drives',0,1,'cpqmib','phydrv',25,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['Compaq Fans',0,1,'cpqmib','fans',26,'AVERAGE','103680',300,1,0,'none',0,1,0,'.',[], [] ],
        ['Compaq Temperature',0,1,'cpqmib','temperature',27,'AVERAGE','103680',300,46,0,'none',0,1,0,'.',[], [] ],
        ['IIS Webserver Information',0,1,'iis_info','',28,'AVERAGE','103680',300,50,0,'none',0,1,0,'.',[], [] ],
        ['Livingston Serial Port',0,1,'livingston_serial_port','',29,'AVERAGE','103680',300,48,0,'none',0,1,0,'.',[], [] ],
        ['Apache',0,1,'apache','',30,'AVERAGE','103680',300,53,0,'none',1,1,0,'',[], [] ],
        ['SQL Query',0,1,'none','',32,'AVERAGE','103680',300,65,0,'none',1,1,0,'',[], [] ],
        ['APC',1,1,'apc','enterprises.318',31,'AVERAGE','103680',300,61,0,'none',0,1,0,'.',[], [] ],
        ['Alteon Real Server',1,1,'alteon_realservers','',33,'AVERAGE','103680',300,66,0,'none',0,1,0,'ent.1872',[], [] ],
        ['Alteon Virtual Server',0,1,'alteon_virtualservers','',34,'AVERAGE','103680',300,70,0,'none',0,1,0,'ent.1872',[], [] ],
        ['Alteon Real Services',0,1,'alteon_realservices','',35,'AVERAGE','103680',300,73,0,'none',0,1,0,'ent.1872',[], [] ],
        ['Alteon System Info',1,1,'host_information','enterprises.1872',36,'AVERAGE','103680',300,75,0,'none',0,1,0,'ent.1872',[], [] ],
        ['Brocade Sensors',0,0,'brocade_sensors','',37,'AVERAGE','103680',300,77,0,'none',0,1,0,'ent.1588',[], [] ],
        ['Brocade FC Ports',0,0,'brocade_fcports','',38,'AVERAGE','103680',300,78,0,'none',0,1,0,'ent.1588',[], [] ],
        ['Cisco Dialup Usage',1,1,'cisco_serial_port','',39,'AVERAGE','103680',300,80,0,'none',0,1,0,'ent.9',[], [] ],
        ['Windows Logical Disks',1,1,'informant_ldisks','',40,'AVERAGE','103680',300,82,0,'none',0,1,0,'.',[], [] ],
        ['UPS',1,1,'ups','',41,'AVERAGE','103680',300,84,0,'none',0,1,0,'.',[], [] ],
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

slas = [
        [u'No SLA',3, u'No SLA',12,100,1],
        [u'Customer Satellite Link',3, u'Customer Sat Link:',12,75,4],
        [u'Main Fiber Link',3, u'Main Link:',12,100,4],
        [u'Main Satellite Link',3, u'Main Sat Link:',12,100,4],
        [u'Cisco Router',3, u'Router:',12,100,3],
        [u'Smokeping Host',3, u'Smokeping:',12,100,14],
        [u'Storage',3, u'Storage',12,100,8],
        [u'Linux/Unix CPU',3, u'',12,100,11],
        [u'Windows CPU',3, u'',12,100,12],
        [u'APC UPS',3, u'APC UPS',12,100,31]
        ]
