# -*- coding: utf-8 -*-
""" Rosenbergs set of attribute discovery plugins"""

# Make sure you list any new plugins below
from alteon import discover_alteon_realservers, discover_alteon_realservices, discover_alteon_virtualservers
from apache import discover_apache
from apc import discover_apc
from bgp import discover_bgp_peers
from cisco_snmp import discover_cisco_envmib, discover_cisco_saagent, discover_pix_connections
from cpqmib import discover_cpqmib
from host_information import discover_host_information
from ntp_client import discover_ntp_client
from reachability import discover_reachability
from sensors import discover_sensors
from snmp import discover_snmp_interfaces, discover_snmp_simple
from snmp_fcport import discover_fc_ports
from snmp_ups import discover_ups, discover_ups_lines
from storage import discover_storage
from tcp_ports import discover_tcp_ports
