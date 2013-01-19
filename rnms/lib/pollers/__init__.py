# -*- coding: utf-8 -*-
""" Rosenbergs set of poller plugins"""

# Make sure you list any new plugins below
from apache import poll_apache
from buffer import poll_buffer
from cisco_accounting import poll_cisco_accounting
from cisco_ping import poll_cisco_snmp_ping_start, poll_cisco_snmp_ping_wait, poll_cisco_snmp_ping_get_pl, poll_cisco_snmp_ping_get_rtt, poll_cisco_snmp_ping_end
from cisco_saagent import poll_cisco_saagent
from hostmib import poll_hostmib_apps, poll_hostmib_perf
from ntp_client import poll_ntp_client
from reach import poll_reach_ping, poll_reach_status
from snmp import poll_snmp_counter, poll_snmp_status, poll_snmp_walk_average
from tcp import poll_tcp_status, poll_snmp_tcp_established, poll_tcp_content
from verify_index import poll_verify_storage_index, poll_verify_interface_number, poll_verify_storage_index, poll_verify_sensor_index

