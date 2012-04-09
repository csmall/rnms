# -*- coding: utf-8 -*-
""" Rosenbergs set of poller plugins"""

# Make sure you list any new plugins below
from apache import run_apache
from snmp import run_snmpget, run_snmp_status

__all__ = [ 'apache', 'run_snmpget', 'run_snmp_status' ]
