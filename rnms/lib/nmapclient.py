# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2015 Craig Small <csmall@enc.com.au>
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
import subprocess
import re
import socket
import os

port_re = re.compile(r'\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*$')
reply_re = re.compile(r'Host: [0-9a-f:.]+\s+\S+\s+Ports: (.+)\s+Ignored State:')

""" nmap subprocess client """

class NmapClient(object):
    nmap_bin = '/usr/bin/nmap'
    logger = None

    def __init__(self, logger):
        self.nmap_ok  = os.access(self.nmap_bin, os.X_OK)
        self.active_scans = {}
        self.logger = logger


    def scan_host(self, scanhost, cb_fun, ports, **kw):
        """
        Start scanning the TCP ports with the popen object
        """
        if self.nmap_ok == False:
            self.logger.debug('No nmap binary found')
            return False
        if port_re.match(ports) is None:
            self.logger.warning('AD Parameter "%s" not a valid port range', ports)
            return False
        try: addrinfo = socket.getaddrinfo(scanhost.mgmt_address, 0)[0]
        except socket.gaierror:
            return False
        nmap_opts = [self.nmap_bin, '-sT', '-p', ports, '-n', '-oG', '-', scanhost.mgmt_address]
        if addrinfo[0] == socket.AF_INET6:
            nmap_opts.insert(1,'-6')
        try:
            p = subprocess.Popen(nmap_opts, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            return False
        self.active_scans[scanhost.mgmt_address] = {
                'popen': p,
                'ipaddr': scanhost.mgmt_address,
                'cb_fun': cb_fun,
                'data': kw,
                }
        return True

    def return_value(self, scan):
        """
        nmap scan has finished so need to reutrn the values
        """
        ret_ports = []
        lines = scan['popen'].communicate()
        for line in lines:
            line_match = reply_re.search(line)
            if line_match:
                raw_ports = line_match.group(1).split(',')
                ret_ports = [ raw_port.split('/') for raw_port in raw_ports]
        if scan['data'] is None:
            scan['cb_fun'](ret_ports, None)
        else:
            scan['cb_fun'](ret_ports, None, **scan['data'])
        del(self.active_scans[scan['ipaddr']])

    def poll(self):
        """
        Regularly run the poll method to check processes are running
        Return number of active scans
        """
        scan_count = 0
        for scan in self.active_scans.values():
            if scan['popen'].poll() is not None:
                self.return_value(scan)
            else:
                scan_count += 1
        return scan_count

