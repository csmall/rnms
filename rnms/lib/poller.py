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
import datetime
from timeit import Timer
import select
import socket
import asyncore
import transaction

from rnms import model
from rnms.lib.snmp import SNMPEngine
from rnms.lib import ntpclient

class Poller():
    """
    Poller process

    poller_buffer is a dict of a dict. The first level is the attribute id
    while the second is dependent on the poller set
    """
    find_attribute_interval = 60 # Scan to find new items every 60secs
    next_find_attribute = 0
    forced_attributes=False

    def __init__(self, attributes=None, logger=None):
        
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger("Poller")
        self.snmp_engine = SNMPEngine(logger=self.logger)
        self.ntp_client = ntpclient.NTPClient(socket.SOCK_DGRAM)
        self.waiting_attributes = [] # Waiting to start
        self.polling_attributes = {} # The attributes we are currently polling
        self.poller_buffer = {}
        self.poller_sets = {} # Cache for polling sets

        if attributes is not None:
            self._add_forced_attributes(attributes)
            self.forced_attributes=True

    def poll(self):
        """
        The poll method for the Poller object.
        It is run at very regular intervals and runs through all the tasks
        that the poller needs to do
        """
        #print select.select([], self.snmp_engine.dispatcher.getSocketMap().keys(), [], self.find_attribute_interval)
        now = datetime.datetime.now()
        retval = False
        if self.forced_attributes == False and self.next_find_attribute < now:
            self.find_new_attributes()
            self.next_find_attribute = now + self.find_attribute_interval
        if self.polling_attributes:
            retval = True
            self.check_polling_attributes()
        if self.snmp_engine.poll():
            retval = True
        if self.ntp_client.poll():
            asyncore.poll(0.2) # FIXME - combine with snmp engine one
            retval = True
        return retval

    def poller_callback(self, attribute, poller_value):
        """
        All real poller callback functions should call this method.
        It is how the real poller lets us know it has come back with
        something, including the value
        """
        try:
            patt = self.polling_attributes[attribute.id]
        except KeyError:
            self.logger.info('A:%d - Poller called back but not in polling attributes', attribute.id)
            return
        try:
            poll_buffer = self.poller_buffer[attribute.id]
        except KeyError:
            self.logger.info('A:%d -: Poller called back but no poller buffer', attribute.id)
            return
        patt['return_time'] = datetime.datetime.now()
        poller_time = patt['return_time'] - patt['start_time']
        poller_time_ms = poller_time.seconds * 1000 + poller_time.microseconds / 1000
        poller_row = self.get_poller_row(patt['attribute'].poller_set_id,patt['index'])
        field_count = len(poller_row.poller.field.split(','))
        #self.logger.debug("A:%d - Poller called back with %d fields", attribute.id, field_count)
        if poller_value is not None:
            if field_count == 1:
                poll_buffer[poller_row.poller.field] = poller_value
            else:
                for ford, fkey in enumerate(poller_row.poller.field.split(',')):
                    try:
                        poll_buffer[fkey] = poller_value[ford]
                    except KeyError:
                        self.logger.warning('A:%d - Field "%s" has no value from poller', attribute.id, fkey)

            poller_row = self.get_poller_row(patt['attribute'].poller_set_id, patt['index'])
            backend_result = poller_row.run_backend(patt['attribute'], poller_value)
            backend_finish_time = datetime.datetime.now()
            backend_time = backend_finish_time - patt['return_time']
            backend_time_ms = backend_time.seconds * 1000 + backend_time.microseconds / 1000
            self.logger.debug("A:%d I:%d - %s:%s -> %s:%s (%d:%d)", patt['attribute'].id, patt['index'], poller_row.poller.display_name, poller_value, poller_row.backend.display_name, backend_result, poller_time_ms, backend_time_ms)
        else:
            self.logger.debug("A:%d I:%d - %s:%s -> N/A (%d:)", patt['attribute'].id, patt['index'], poller_row.poller.display_name, poller_value, poller_time_ms )

        # Run the next poll row
        patt['index'] += 1
        patt['in_poller'] = False

    def check_polling_attributes(self):
        """
        Run through the set of polling_attributes and kick of the next
        queries, when required
        """
        for att_id,patt in self.polling_attributes.items():
            if patt['in_poller'] == True:
                continue
            if patt['index'] == 0:
                self.poller_buffer[att_id] = {}
            patt['in_poller'] = True # must be pre-set for race of fast pollers
            self._run_poller(patt)

    def _run_poller(self, patt):
        """
        Run the actual poller
        """
        patt['start_time'] = datetime.datetime.now()
        poller_row = self.get_poller_row(patt['attribute'].poller_set_id, patt['index'])
        if poller_row is None:
            self._finish_polling(patt)
            return
        if not poller_row.run_poller(self, patt['attribute'], self.poller_buffer[patt['attribute'].id]): # run was successful
            self.logger.warn('A:%d - row %d Poller run failed', patt['attribute'].id, patt['index'])
            self._finish_polling(patt)


    def _finish_polling(self, patt):
        """
        Complete all the finishing up that is required once a poller has
        run through its entire set of PollerRows
        """
        # Update all the relevant RRD files
        updated_rrds = []
        rrd_fields = model.DBSession.query(model.AttributeTypeRRD).filter(model.AttributeTypeRRD.attribute_type_id == patt['attribute'].attribute_type_id)
        for rrd_field in rrd_fields:
            if rrd_field.name in self.poller_buffer[patt['attribute'].id]:
                updated_rrds.append('{0}:{1}'.format(rrd_field.name,
                    rrd_field.update(patt['attribute'], self.poller_buffer[patt['attribute'].id][rrd_field.name])))
        if len(updated_rrds) > 0:
            self.logger.debug('A:%d - Polling complete - rrds: %s', patt['attribute'].id, ', '.join(updated_rrds))
        else:
            self.logger.debug('A:%d - Polling complete - no rrds', patt['attribute'].id)
        del (self.poller_buffer[patt['attribute'].id])
        del (self.polling_attributes[patt['attribute'].id])
        model.DBSession.flush()

    def _add_forced_attributes(self, att_ids):
        """
        Add these attributes even if theyre not ready for polling.
        Method expects a list of attribute IDs
        """
        assert(type(att_ids) == list)
        attributes = model.DBSession.query(model.Attribute).filter(model.Attribute.id.in_(att_ids))
        for attribute in attributes:
            self.attribute_add(attribute)


    def find_new_attributes(self):
        """
        Scan the attribute table and look for any attributes that need polling
        """
        hosts_down = {}
        self.logger.debug("Scanning attribute table to find new items to poll")
        now = datetime.datetime.now()
        attributes = model.DBSession.query(model.Attribute).filter(and_(
                (model.Attribute.next_poll < now),
                (model.Attribute.poll_priority==True),
                (model.Attribute.poller_set_id > 1))).order(model.Attribute.polled)
        for attribute in attributes:
            # Skip if already polling
            if attribute.id in self.polling_attributes:
                continue

            # Skip if not main attribute and main atts down
            if attribute.poll_priority == False:
                if attribute.host_id not in  hosts_down:
                    hosts_down[attribute.host_id] = attribute.host.main_attributes_down()
                if hosts_down[attribute.host_id]:
                    continue
            self.attribute_add(attribute)

    def attribute_add(self, attribute):
        """
        Add the given attribute to the polled_attributes list the poller
        keeps. Also resets the pointers to first poller_set row
        """
        self.polling_attributes[attribute.id] = {
                'attribute': attribute,
                'index': 0,
                'in_poller': False
                }

    def get_poller_row(self, poller_set_id, row_index):
        """
        Return the row specified in the index from the poller_set
        If not already cached then update cache with it
        If there is no such poller set OR row from set return None
        """
        try:
            poller_set = self.poller_sets[poller_set_id]
        except KeyError:
            if self.cache_poller_set(poller_set_id):
                poller_set = self.poller_sets[poller_set_id]
            else:
                self.logger.info("PollerSet #%d not found",poller_set_id)
                return None
        try:
            poller_row = poller_set[row_index]
        except IndexError:
            return None
        return poller_row


    def cache_poller_set(self, poller_set_id):
        """
        Cache the given PollerSet within the Poller object so each
        attribute using this set has it
        returns true if it is found
        """
        
        if poller_set_id in self.poller_sets:
            return True

        poller_set = model.PollerSet.by_id(poller_set_id)
        if poller_set is None:
            return False
        self.poller_sets[poller_set_id] = [ poller_row for poller_row in poller_set.poller_rows]
        return True

