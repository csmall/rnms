# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012,2013 Craig Small <csmall@enc.com.au>
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
import datetime
import transaction

from sqlalchemy import and_
from sqlalchemy.exc import DBAPIError

from rnms import model
from rnms.lib.engine import RnmsEngine
from rnms.lib.snmp import SNMPRequest
from rnms.lib.pollers.snmp import parse_oid, cb_snmp_counter, split_oid
from rnms.lib.rrdworker import RRDClient

"""
There are multiple timers that are used to work out when to do various
functions for a poller:
    SCAN_TABLE_SECONDS is the amount of time we search the Attribute table
      looking for NEW attributes to add to the polling list
    POLLER_WINDOW_SECONDS is how far into the future we look for Attributes
      that need to be polled. This stops us from polling one item, sleeping
      sat 2 seconds and hitting the database again
"""
SCAN_TABLE_SECONDS = 60 
POLLER_WINDOW_SECONDS = 10 
                          
class Poller(RnmsEngine):
    """
    Poller process

    poller_buffer is a dict of a dict. The first level is the attribute id
    while the second is dependent on the poller set
    """
    NEED_CLIENTS = ('ntp', 'ping', 'snmp', 'tcp')
    do_once = True
    find_attribute_interval = 60 # Scan to find new items every 60secs
    next_find_attribute = datetime.datetime.min
    forced_attributes=False
    host_ids = None
    poller_buffer = None
    rrd_client = None

    def __init__(self, attribute_ids=None, host_ids=None, zmq_context=None, do_once=True):
        super(Poller, self).__init__('poller', zmq_context)
        
        self.rrd_client = RRDClient(self.zmq_context, self.zmq_core)
        self.polling_attributes = {} # The attributes we are currently polling
        self.poller_buffer = {}
        self.poller_sets = {} # Cache for polling sets

        if attribute_ids is not None or host_ids is not None:
            self._add_forced_attributes(attribute_ids, host_ids)
            self.forced_attributes=True
        self.do_once = do_once

    def main_loop(self):
        """
        The main loop for the poller to do everything it needs to do.
        This will only exit if we have forced attributes and they are
        all polled.
        """
        while True:
            now = datetime.datetime.now()
            polls_running = False
            if self.forced_attributes == False and self.next_find_attribute < now:
                self.find_new_attributes()
                self.next_find_attribute = now + datetime.timedelta(seconds=self.find_attribute_interval)
            att_count = len(self.polling_attributes)
            if self.polling_attributes:
                self.check_polling_attributes()
                polls_running = True
            snmp_jobs = self.snmp_engine.poll()
            if snmp_jobs > 0:
                att_count -= snmp_jobs
            ntp_jobs = self.ntp_client.poll()
            att_count -= ntp_jobs
            tcp_jobs = self.tcp_client.poll()
            att_count -= tcp_jobs

            # Ping jobs is the only one that doesn't use zmqcore, bah (yet)
            ping_jobs =  self.ping_client.poll() 
            if ping_jobs > 0:
                att_count -= ping_jobs

            if self.zmq_core.poll(0.0) == False:
                return
            if not polls_running and (self.polling_attributes == {}):
                # If there are no pollers, we can sleep until we need to
                # look for more attributes to poll
                self.poller_sets = {}

                if self.do_once == True or self.end_thread == True:
                    break
                transaction.commit()
                if self._sleep_until_next() == False:
                    return
        self.wait_for_workers()
        transaction.commit()

    def poller_callback(self, attribute_id, poller_row, poller_value):
        """
        All real poller callback functions should call this method.
        It is how the real poller lets us know it has come back with
        something, including the value
        """
        try:
            patt = self.polling_attributes[attribute_id]
        except KeyError:
            self.logger.info('A:%d - Poller called back but not in polling attributes', attribute_id)
            return
        try:
            poll_buffer = self.poller_buffer[attribute_id]
        except KeyError:
            self.logger.info('A:%d -: Poller called back but no poller buffer', attribute_id)
            return
        patt['return_time'] = datetime.datetime.now()
        poller_time = patt['return_time'] - patt['start_time']
        poller_time_ms = poller_time.seconds * 1000 + poller_time.microseconds / 1000
        #poller_row = self.get_poller_row(patt['attribute'].poller_set_id,patt['index'])
            #self.logger.debug("A:%d - Poller called back with %d fields", attribute.id, field_count)
        if poller_value is not None:
            if poller_row.poller.field != '':
                field_count = len(poller_row.poller.field.split(','))
                if field_count == 1:
                    poll_buffer[poller_row.poller.field] = poller_value
                else:
                    for ford, fkey in enumerate(poller_row.poller.field.split(',')):
                        try:
                            poll_buffer[fkey] = poller_value[ford]
                        except KeyError:
                            self.logger.warning('A:%d - Field "%s" has no value from poller', attribute_id, fkey)

            #poller_row = self.get_poller_row(patt['attribute'].poller_set_id, patt['index'])
            poller_result = self._poller_prettyprint(poller_value)
            backend_result = poller_row.run_backend(patt['attribute'], poller_value)
            backend_finish_time = datetime.datetime.now()
            backend_time = backend_finish_time - patt['return_time']
            backend_time_ms = backend_time.seconds * 1000 + backend_time.microseconds / 1000
            self.logger.debug("A:%d I:%d - %s:%s -> %s:%s (%d:%d)", attribute_id, poller_row.position, poller_row.poller.display_name, poller_result, poller_row.backend.display_name, backend_result, poller_time_ms, backend_time_ms)
        else:
            self.logger.debug("A:%d I:%d - %s:%s -> N/A (%d:)", attribute_id, poller_row.position, poller_row.poller.display_name, poller_value, poller_time_ms )

        # Run the next poll row
        patt['in_poller'] = False
    
    def _poller_prettyprint(self, poller_value):
        """
        Print a nice output of the returned value from the poller for debugging
        """
        max_len=100
        val_type = type(poller_value)
        if val_type == str or val_type == unicode:
            retval = str(poller_value)
        elif val_type == int or val_type == float:
            retval = str(poller_value)
        elif val_type == list or val_type == tuple:
            retval = u','.join([unicode(x) for x in poller_value])
        elif val_type == dict:
            retval = u','.join([str(x) for x in poller_value.values()])
        else:
            retval = poller_value
        return retval[:max_len]


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
            if patt['index'] not in patt['skip_rows']:
                self._run_poller(patt)
            patt['index'] += 1

    def _run_poller(self, patt):
        """
        Run the actual poller
        """
        patt['in_poller'] = True
        patt['start_time'] = datetime.datetime.now()
        poller_row = self.get_poller_row(patt['attribute'].poller_set_id, patt['index'])
        if poller_row is None:
            self._finish_polling(patt)
            return
        # Special speed-up for snmp fetch, get it all in one group
        # This does NOT work for SNMP v1, or this implementaiton anyhow
        if poller_row.poller.command == 'snmp_counter' and not patt['attribute'].host.ro_is_snmpv1() :
            patt['skip_rows'] = self._multi_snmp_poll(patt)
            if patt['skip_rows'] != []:
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
            if rrd_field.name in self.poller_buffer[patt['attribute'].id] and self.poller_buffer[patt['attribute'].id][rrd_field.name] is not None:
                updated_rrds.append('{0}:{1}'.format(rrd_field.name,
                    rrd_field.update(patt['attribute'], self.poller_buffer[patt['attribute'].id][rrd_field.name], rrd_client=self.rrd_client)))
        self.logger.info('A:%d - Polling complete - rrds: %s', patt['attribute'].id, ', '.join(updated_rrds))
        del (self.poller_buffer[patt['attribute'].id])
        del (self.polling_attributes[patt['attribute'].id])
        patt['attribute'].update_poll_time()
        try:
            model.DBSession.flush()
        except DBAPIError as err:
            self.logger.warning(
                'A:%d - Database Error %s'.format(
                    err, patt['attribute'].id))

    def _add_forced_attributes(self, attribute_ids=None, host_ids=None):
        """
        Add these attributes even if theyre not ready for polling.
        Method expects a list of attribute IDs or host_ids
        """
        if attribute_ids is not None:
            assert(type(attribute_ids) == list )
            for attribute in model.DBSession.query(model.Attribute).filter(model.Attribute.id.in_(attribute_ids)):
                self.attribute_add(attribute)
        if host_ids is not None:
            assert(type(host_ids) == list )
            for attribute in model.DBSession.query(model.Attribute).filter(model.Attribute.host_id.in_(host_ids)):
                self.attribute_add(attribute)


    def find_new_attributes(self):
        """
        Scan the attribute table and look for any attributes that need polling
        """
        hosts_down = {}
        self.logger.debug("Scanning attribute table to find new items to poll")
        next_poll_limit = datetime.datetime.now() + datetime.timedelta(seconds=POLLER_WINDOW_SECONDS)
        attributes = model.DBSession.query(model.Attribute).filter(and_(
                (model.Attribute.next_poll < next_poll_limit),
                (model.Attribute.poll_enabled == True))).order_by(model.Attribute.next_poll)
        if self.host_ids is not None:
            attributes = attributes.filter(model.Attribute.host_id.in_(self.host_ids))
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
                'in_poller': False,
                'skip_rows' : [],
                }

    def get_poller_set(self, poller_set_id):
        try:
            return self.poller_sets[poller_set_id]
        except KeyError:
            if self.cache_poller_set(poller_set_id):
                return self.poller_sets[poller_set_id]
            else:
                self.logger.info("PollerSet #%s not found",poller_set_id)
        return None

    def get_poller_row(self, poller_set_id, row_index):
        """
        Return the row specified in the index from the poller_set
        If not already cached then update cache with it
        If there is no such poller set OR row from set return None
        """
        poller_set = self.get_poller_set(poller_set_id)
        if poller_set is None:
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

    def _multi_snmp_poll(self, patt):
        """
        This fast-forwards all SNMP queries into one request which should
        speed up the poller with SNMP heavy requests. The flip-side is that
        the strict poller order is not maintained
        """
        skip_rows = []
        #self.logger.debug("A#%d: multi_snmp start",patt['attribute'].id)
        poller_set = self.get_poller_set(patt['attribute'].poller_set_id)
        if poller_set is None:
            return []
        req = SNMPRequest(patt['attribute'].host)
        for poller_row in poller_set:
            if poller_row.position < patt['index']:
                continue
            if poller_row.poller.command == 'snmp_counter':
                oid = parse_oid(split_oid(poller_row.poller.parsed_parameters(patt['attribute']), patt['attribute'].host))
                if oid is not None:
                    data = {'pobj': self, 'poller_row': poller_row, 'attribute': patt['attribute']}
                    req.add_oid(oid, cb_snmp_counter, data=data)
                    skip_rows.append(poller_row.position)
        if req.oids == []:
            return skip_rows
        patt['in_poller'] = True
        patt['start_time'] = datetime.datetime.now()
        self.snmp_engine.get(req)
        return skip_rows

    def _sleep_until_next(self):
        """
        Stay in this loop until we need to go into the main loop again.
        Returns False if we have broken out of the poll
        """
        next_attribute = model.Attribute.next_polled()
        if next_attribute is None:
            return self.sleep(self.next_find_attribute)
        else:
            self.logger.info("Next polled attribute #%d at %s", next_attribute.id, next_attribute.next_poll.ctime())
            if self.next_find_attribute > next_attribute.next_poll:
                self.next_find_attribute = next_attribute.next_poll
            return self.sleep(self.next_find_attribute)

    def have_working_workers(self):
        return self.rrd_client.has_jobs()

