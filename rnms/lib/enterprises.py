# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
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

"""
Module for interpreting SNMP Enterprises in a sensible way.
The raw data comes from https://www.iana.org/assignments/enterprise-numbers
but it suffers from not being updated or using funny names for enterprises,
such as enterprise 9 ciscoSystems instead of Cisco.
"""

__all__ = ['enterprise_name', 'oid2enterprise_name']

def enterprise_name(ent_id):
    """
    Converts the ent_id which is an integer for the enterprise ID
    into a string describe the enterprise.
    """
    return enterprises[ent_id]

def oid2enterprise_name(oid):
    """
    Convert the given oid in numeric "1.3.6.1.4.1.X" or short "ent.X"
    form into an enterprise name.
    """
    if oid is None:
        return 'Unknown'
    if oid[:4] == 'ent.':
        idx = 1
        offset = 4
    elif oid[:10] == '1.3.6.1.4.1.':
        idx = 6
        offset = 10
    else:
        return 'Unknown'

    # First try systemobjectid
    try:
        return system_object_ids[oid[offset:]]
    except KeyError:
        pass
    oid_digits = oid.split('.')
    try:
        ent_id = int(oid_digits[idx])
    except (ValueError,IndexError):
        return 'Unknown'
    try:
        return enterprise_name(ent_id)
    except KeyError:
        return 'Unknown ID '+ str(ent_id)

enterprises = {
        2:      'IBM',
        9:      'Cisco',
        11:     'HP',
        42:     'Sun',
        43:     'HP/3Com',
        52:     'Enterasys',
        63:     'Apple',
        94:     'Nokia',
        106:    'EMC',
        111:    'Oracle',
        116:    'Hitachi',
        123:    'Newbridge',
        161:    'Motorolla',
        164:    'RAD Data Communications',
        171:    'D-Link',
        191:    'NCR',
        193:    'Ericsson',
        207:    'Allied Telesyn',
        288:    'EDS',
        289:    'Brocade',
        297:    'Fuji Xerox',
        311:    'Microsoft',
        318:    'APC',
        370:    'HP/3COM',
        582:    'Cisco',
        872:    'AVM',
        1230:   'McAfee',
        1573:   'McAfee',
        1588:   'Brocade',
        1872:   'Alteon',
        2011:   'Huawei',
        2636:   'Juniper',
        3401:   'McAfee',
        3902:   'ZTE',
        5771:   'Cisco',
        5842:   'Cisco',
        6876:   'VMware',
        7031:   'McAfee',
        8072:   'Net-SNMP',
        11147:  'HP',
        14823:  'Aruba',
        22252:  'McAfee',
        25506:  'H3C',
        26484:  'Cisco',
        }

system_object_ids = {
        # Juniper
        '2636.1.1.1.2.1':   'Juniper M20',
        '2636.1.1.1.2.2':   'Juniper M20',
        '2636.1.1.1.2.3':   'Juniper M160',
        '2636.1.1.1.2.4':   'Juniper M10',
        '2636.1.1.1.2.5':   'Juniper M5',
        '2636.1.1.1.2.6':   'Juniper T640',
        '2636.1.1.1.2.7':   'Juniper T320',
        '2636.1.1.1.2.8':   'Juniper M40e',
        '2636.1.1.1.2.9':   'Juniper M320',
        '2636.1.1.1.2.10':  'Juniper M7i',
        '2636.1.1.1.2.11':  'Juniper M10i',
        '2636.1.1.1.2.13':  'Juniper J2300',
        '2636.1.1.1.2.14':  'Juniper J4300',
        '2636.1.1.1.2.15':  'Juniper J6300',
        '2636.1.1.1.2.17':  'Juniper TX',
        '2636.1.1.1.2.18':  'Juniper M120',
        '2636.1.1.1.2.21':  'Juniper MX960',
        '2636.1.1.1.2.25':  'Juniper MX480',
        '2636.1.1.1.2.26':  'Juniper SRX5800',
        '2636.1.1.1.2.28':  'Juniper SRX5600',
        '2636.1.1.1.2.29':  'Juniper MX240',
        '2636.1.1.1.2.30':  'Juniper EX3200',
        '2636.1.1.1.2.31':  'Juniper EX4200',
        '2636.1.1.1.2.32':  'Juniper EX8208',
        '2636.1.1.1.2.33':  'Juniper EX8216',
        '2636.1.1.1.2.34':  'Juniper SRX3600',
        '2636.1.1.1.2.35':  'Juniper SRX3400',
        '2636.1.1.1.2.36':  'Juniper SRX210',
        '2636.1.1.1.2.37':  'Juniper SRX240',
        '2636.1.1.1.2.38':  'Juniper SRX650',
        '2636.1.1.1.2.41':  'Juniper SRX100',
        '2636.1.1.1.2.42':  'Juniper ESR1000V',
        '2636.1.1.1.2.43':  'Juniper EX2200',
        '2636.1.1.1.2.44':  'Juniper EX4500',
        '2636.1.1.1.2.44':  'Juniper EX4500',
        '2636.1.1.1.2.49':  'Juniper SRX1400',
        '2636.1.1.1.2.57':  'Juniper MX80',
        '2636.1.1.1.2.58':  'Juniper SRX220',
        '2636.1.1.1.2.58':  'Juniper EX XRE',
        '2636.1.1.1.2.60':  'Juniper QFX Interconnect',
        '2636.1.1.1.2.61':  'Juniper QFX Node',
        '2636.1.1.1.2.64':  'Juniper SRX110',

        '8072.3.2.1':       'HP-UX 9',
        '8072.3.2.2':       'SunOS 4',
        '8072.3.2.3':       'Solaris',
        '8072.3.2.4':       'OSF',
        '8072.3.2.5':       'Ultrix',
        '8072.3.2.6':       'HP-UX 10',
        '8072.3.2.7':       'NetBSD',
        '8072.3.2.8':       'FreeBSD',
        '8072.3.2.9':       'Irix',
        '8072.3.2.10':      'Linux',
        '8072.3.2.11':      'BSDi',
        '8072.3.2.12':      'OpenBSD',
        '8072.3.2.13':      'Windows',
        '8072.3.2.14':      'HP-UX 11',
        '8072.3.2.15':      'AIX',
        '8072.3.2.16':      'MacOS',
        '8072.3.2.17':      'Unknown net-snmp',
        }
