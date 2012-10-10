# -*- coding: utf-8 -*-
""" Rosenbergs set of poller plugins"""

# Make sure you list any new plugins below
from apache import run_apache
from cisco_ping import poll_cisco_snmp_ping_start, poll_cisco_snmp_ping_wait, poll_cisco_snmp_ping_get_pl, poll_cisco_snmp_ping_get_rtt, poll_cisco_snmp_ping_end
from ntp_client import poll_ntp_client
from snmp import poll_snmp_counter, poll_snmp_status
from tcp import poll_tcp_status
from verify_index import poll_verify_storage_index, poll_verify_interface_number

