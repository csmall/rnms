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
    The SNMP Scheuduler is given a series of SNMP polling jobs and stores 
    them.  When the poller needs more items to poll, the scheduler determines
    the best items to use, dependent on what is currently been polling.
    """

    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger("SNMPScheduler")
        else:
            self.logger = logger
        self.waiting_jobs = []
        self.active_jobs = {}
        self.active_addresses = {}

    def job_update(self, oldid, newid):
        """
        For getnext methods we run the same request over and over. This
        method updates the ID and sends the updated request again.
        """
        if oldid not in self.active_jobs:
            self.logger.warn("Trying to update job {0} but not found.".format(oldid))
            return False
        self.active_jobs[newid] = self.active_jobs[oldid]
        del self.active_jobs[oldid]
        self.active_jobs[newid]['id'] = newid

    def job_add(self, reqid,  request, msg, table_oid = None, table_trim=None):
        """
        Adds a new job to the waiting queue
        """
        self.waiting_jobs.append({
            'id': reqid,
            'host' : request.host,
            'request': request,
            'msg': msg,
            'table_oid' : table_oid,
            'table_trim': table_trim,
            })

            

    def job_del_by_host(self, host):
        """
        Delete all jobs in waiting and active queue for the given host
        """
        if host.mgmt_address in self.active_addresses:
            for job in self.active_jobs:
                if job.host.mgmt_address == host.mgmt_address:
                    self.address_del(host.mgmt_address)
                    del(self.active_jobs[job.jobid])

        for i,job in self.waiting_jobs:
            if job.host.mgmt_address == host.mgmt_address:
                del(self.waiting_jobs[i])

    def job_pop(self):
        """
        Returns the "best" job to be polled next, depending what the
        scheduler decides is "best". Returns None if there are no best
        items.

        Callers should deal with each job first, for example calling
        job_sent() before calling this method again.
        """
        for job in self.waiting_jobs:
            if job['host'].mgmt_address not in self.active_addresses:
                #self.logger.debug("job_pop(): Poping job {0}".format(job['id']))
                return job
        return None


    def job_sent(self, reqid):
        """
        The Engine needs to tell the Scheduler that the job has been
        sent. This will put this job into the active list and out
        of pending list.
        """
        for i,job in enumerate(self.waiting_jobs):
            if job['id'] == reqid:
                self.address_add(job['host'].mgmt_address)
                self.active_jobs[reqid] = job
                del(self.waiting_jobs[i])
                return

    def job_received(self, reqid):
        """
        The Engine calls this when either there has been a reply OR
        the Engine has given up on trying to poll this item.  In any
        case it frees up the polling of the remote device.
        """
        #self.logger.debug("Scheduler attempting to remove request {0}".format(reqid))
        if reqid in self.active_jobs:
            job = self.active_jobs[reqid]
            mgmt_address = job['host'].mgmt_address
            self.address_del(mgmt_address)
            del(self.active_jobs[reqid])

    def have_active_jobs(self):
        return self.active_jobs != {}

    def have_waiting_jobs(self):
        return self.waiting_jobs != []

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

