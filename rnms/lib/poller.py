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

from rnms.model import Attribute

class Poller():
    """
    Poller process

    poller_buffer is a dict of a dict. The first level is the attribute id
    while the second is dependent on the poller set
    """
    poller_buffer = {}
    polling_attributes = {} # The attributes we are currently polling
    polling_sets = {} # Cache for polling sets
    find_attribute_interval = 60 # Scan to find new items every 60secs
    next_find_attribute = 0

    def __init__(self, logger=None):
        
        self.snmp_engine = SNMPEngine(logger=logger)
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger("Poller")

    def poll_finished(self,attribute):
        """
        This method is called once a poller has finished running
        and needs to signal to move to the next one
        """
        if attribute.id not in self.polling_attributes:
            # FIXME logger
            return
        patt = self.polling_attributes[attribute.id]
        patt['index'] += 1
        self._run_poller(patt)

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
        if self.polling_attributes:
            self.check_pollers()
        self.snmp_engine.poll()

    def check_polling_attributes(self):
        """
        Run through the set of polling_attributes and kick of the next
        queries, when required
        """
        for att_id,patt in self.polling_attributes.items():
            if patt['in_poller']:
                next
            if patt['index'] == 0:
                self.poller_buffer[att_id] = {}
            else:
                patt['index'] += 1
            self._run_poller(patt)

    def _run_poller(self, patt):
        """
        Run the actual poller
        """
        poller_row = self.get_poller_row(patt['attribute'].poller_set_id], patt['index'])
        if poller_row is None:
            self._finish_polling(patt)
            return
        if poller_row.run(patt['attribute'], self.poller_buffer[patt['attribute'].id]): # run was successful
            patt['in_poller'] = True

    def _finish_polling(self, patt):
        """
        Complete all the finishing up that is required once a poller has
        run through its entire set of PollerRows
        """
        # Update all the relevant RRD files
        updated_rrds = {}
        rrd_fields = DBSession.query(model.AttributeTypeRRD)filter(model.AttributeTypeRRD== patt['attribute'].attribute_type_id)
        for rrd_field in rrd_fields:
            if rrd_field.name in self.poller_buffer[patt['attribute'].id]:
                rrd_field.update(patt['attribute'], self.poller_buffer[patt['attribute'].id])
        del self.poller_buffer[patt['attribute'].id]
        del self.polling_attributes[patt['attribute'].id]

    def find_new_attributes(self):
        """
        Scan the attribute table and look for any attributes that need polling
        """
        hosts_down = {}
        self.logger.debug("Scanning attribute table to find new items to poll")
        now = datetime.datetime.now()
        attributes = model.DBSession(Attribute).filter(and_(
                (Attribute.next_poll < now),
                (Attribute.poll_priority==True),
                (Attribute.poller_set_id > 1))).order(Attribute.polled)
        for attribute in attributes:
            # Skip if already polling
            if attribute.id in self.polling_attributes:
                next

            # Skip if not main attribute and main atts down
            if attribute.poll_priority == False:
                if attribute.host_id not in  hosts_down:
                    hosts_down[attribute.host_id] = attribute.host.main_attributes_down()
                if hosts_down[attribute.host_id]:
                    next
            self.attribute_add(attribute)

    def attribute_add(self, attribute):
        """
        Add the given attribute to the polled_attributes list the poller
        keeps. Also resets the pointers to first poller_set row
        """
        self.polling_attributes[attribute.id] = {
                'attribute': attribute,
                'poller_set': self.poller_sets[attribute.poller_set_id],
                'index': 0,
                'in_poller': False
                }

    def cache_poller_set(self, poller_set_id):
        """
        Cache the given PollerSet within the Poller object so each
        attribute using this set has it
        returns true if it is found
        """
        
        if poller_set_id in self.poller_sets:
            return True

        db_poller_set = PollerSet.by_id(poller_set_id)
        if poller_set is None:
            return False
        self.poller_sets[poller_set_id] = [ poller_row for poller_row in poller_set.poller_rows]
        return True

