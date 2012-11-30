# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012 Craig Small <csmall@enc.com.au>
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
import logging
import subprocess
import re

logger = logging.getLogger('ping')

""" ping Client """

class PingClient():
    """
    Base client to send and receive pings using fping
    """
    fping_bin='/usr/bin/fping'
    fping_re = re.compile(r'\S+ : xmt\/rcv\/%loss = [0-9]+\/[0-9]+\/([0-9.]+)%(?:, min\/avg\/max = [0-9.]+\/([0-9.]+)\/[0-9]+)?')

    def __init__(self):
        self.active_pings = {}

    def ping_host(self, host, cb_fun, num_pings, interval, **kw):
        """
        Start the ping, return the popen object on success or None on error
        """
        ipaddr = host.mgmt_address

        try:
            p = subprocess.Popen([self.fping_bin, '-c', str(num_pings), '-p', str(interval), '-q', ipaddr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            return False
        self.active_pings[ipaddr] = {
                'popen': p,
                'ipaddr': ipaddr,
                'cb_fun': cb_fun,
                'data' : kw,
                }
        return True

    def return_value(self, ping):
        """
        ping has finished, send the callback the data
        values are (rtt,packetloss)
        """
        (ping_out, ping_err) = ping['popen'].communicate()
        match = self.fping_re.search(ping_err)
        if match:
            values = (float(match.group(2)), float(match.group(1)))
            if ping['data'] is None:
                ping['cb_fun'](values, None)
            else:
                ping['cb_fun'](values, None, **ping['data'])
        del(self.active_pings[ping['ipaddr']])

    def poll(self):
        """
        Regularly run the poller to check processes are running
        Return number of active pings
        """
        ping_count = 0
        for ping in self.active_pings.values():
            if ping['popen'].poll() is not None:
                self.return_value(ping)
            else:
                ping_count += 1
        return ping_count




