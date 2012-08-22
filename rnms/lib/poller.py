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
import time

class Poller():
    """
    Poller process

    poller_buffer is a dict of a dict. The first level is the attribute id
    while the second is dependent on the poller set
    """

    poller_buffer = {}
    find_attribute_interval = 60 # Scan to find new items every 60secs
    next_find_attribute = 0

    def __init__(self, logger=None):
        
        self.snmp_engine = SNMPEngine(logger=logger)
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger("Poller")


    def poll(self):
        """
        The poll method for the Poller object.
        It is run at very regular intervals and runs through all the tasks
        that the poller needs to do
        """
        now = time.time()
        if self.next_find_attribute < now:
            self.find_new_attributes()
            self.next_find_attribute = now + self.find_attribute_interval
        self.snmp_engine.poll()

    def find_new_attributes(self):
        """
        Scan the attribute table and look for any attributes that need polling
        """
        self.logger.debug("Scanning attribute table to find new items to poll")
        attributes = model.DBSession(model.Attribute).filter
