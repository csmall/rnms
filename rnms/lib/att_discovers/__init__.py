# -*- coding: utf-8 -*-
""" Rosenbergs set of attribute discovery plugins"""

# Make sure you list any new plugins below
from alteon import discover_alteon_realservers, discover_alteon_realservices, discover_alteon_virtualservers
from apache import discover_apache
from apc import discover_apc
from bgp import discover_bgp_peers
from cisco_snmp import discover_cisco_envmib, discover_cisco_saagent
from cpqmib import discover_cpqmib
from host_information import discover_host_information
from ntp_client import discover_ntp_client
from reachability import discover_reachability
from snmp import discover_snmp_interfaces, discover_snmp_simple
from storage import discover_storage
