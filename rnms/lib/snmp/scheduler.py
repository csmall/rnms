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
""" SNMP Scheduler """
import logging

class SNMPScheduler():
    """
    The SNMP Scheuduler is given a series of SNMP polling requests and stores 
    them.  When the poller needs more items to poll, the scheduler determines
    the best items to use, dependent on what is currently been polling.
    """

    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger("SNMPScheduler")
        else:
            self.logger = logger
        self.waiting_requests = []
        self.active_requests = {}
        self.active_addresses = {}

    def request_update(self, oldid, newid):
        """
        For getnext methods we run the same request over and over. This
        method updates the ID and sends the updated request again.
        """
        if oldid not in self.active_requests:
            self.logger.warn("Trying to update request {0} but not found.".format(oldid))
            return False
        self.active_requests[newid] = self.active_requests[oldid]
        del self.active_requests[oldid]
        self.active_requests[newid].id = newid

    def request_add(self, request):
        """
        Adds a new request to the waiting queue
        """
        self.waiting_requests.append(request)
            

    def request_del_by_host(self, host):
        """
        Delete all requests in waiting and active queue for the given host
        """
        if host.mgmt_address in self.active_addresses:
            for request in self.active_requests:
                if request.host.mgmt_address == host.mgmt_address:
                    self.address_del(host.mgmt_address)
                    del(self.active_requests[request.requestid])

        for i,request in self.waiting_requests:
            if request.host.mgmt_address == host.mgmt_address:
                del(self.waiting_requests[i])

    def request_pop(self):
        """
        Returns the "best" request to be polled next, depending what the
        scheduler decides is "best". Returns None if there are no best
        items.

        Callers should deal with each request first, for example calling
        request_sent() before calling this method again.
        """
        for request in self.waiting_requests:
            if request.host.mgmt_address not in self.active_addresses:
                #self.logger.debug("request_pop(): Poping request {0}".format(request['id']))
                return request
        return None


    def request_sent(self, reqid):
        """
        The Engine needs to tell the Scheduler that the request has been
        sent. This will put this request into the active list and out
        of pending list.
        """
        for idx,request in enumerate(self.waiting_requests):
            if request.id == reqid:
                self.address_add(request.host.mgmt_address)
                self.active_requests[reqid] = request
                del(self.waiting_requests[idx])
                return

    def request_received(self, reqid):
        """
        The Engine calls this when either there has been a reply OR
        the Engine has given up on trying to poll this item.  In any
        case it frees up the polling of the remote device.
        """
        #self.logger.debug("Scheduler attempting to remove request {0}".format(reqid))
        if reqid in self.active_requests:
            request = self.active_requests[reqid]
            mgmt_address = request.host.mgmt_address
            self.address_del(mgmt_address)
            del(self.active_requests[reqid])

    def have_active_requests(self):
        return self.active_requests != {}

    def have_waiting_requests(self):
        return self.waiting_requests != []

    def address_add(self, address):
        """
        Add the given address to the active address list
        """
        if address in self.active_addresses:
            self.active_addresses[address] += 1
        else:
            self.active_addresses[address] = 1

    def address_del(self, address):
        """
        Delete the given address from the active_addresses list
        """
        if address not in self.active_addresses:
            return

        if self.active_addresses[address] == 1:
            del(self.active_addresses[address])
        else:
            self.active_addresses[address] -= 1

