# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2014 Craig Small <csmall@enc.com.au>
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
import time
import transaction

from sqlalchemy import and_

from rnms import model
from rnms.model import DBSession
from rnms.lib.engine import RnmsEngine
from rnms.lib.snmp import SNMPRequest
from plugins.snmp import parse_oid, cb_snmp_counter, split_oid
from rnms.lib.rrdworker import RRDClient
from rnms.lib.gettid import gettid
from rnms.lib.backend import CacheBackend

#from poller_model import CachePoller, CacheHost, CacheAttribute
from poller_model import CacheAttribute, CachePoller
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
    find_attribute_interval = 60  # Scan to find new items every 60secs
    forced_attributes = False
    host_ids = None
    poller_buffer = None
    rrd_client = None

    def __init__(self, attribute_ids=None, host_ids=None, zmq_context=None,
                 do_once=True):
        super(Poller, self).__init__('rnms.poll', zmq_context)
        self.next_find_attribute = datetime.datetime.min

        self.rrd_client = RRDClient(self.zmq_context, self.zmq_core)
        self.polling_attributes = {}  # The attributes we are currently polling
        self.poller_buffer = {}
        self.backends = {}
        self.load_config()

        if attribute_ids is not None or host_ids is not None:
            self._add_forced_attributes(attribute_ids, host_ids)
            self.forced_attributes = True
        self.do_once = do_once

    def load_config(self):
        """ Load the configuration from the Database """
        self.pollers = {
            p.id: CachePoller(p) for p in
            model.DBSession.query(model.Poller)}

        self.backends = {
            b.id: CacheBackend(b) for b in
            model.DBSession.query(model.Backend)}
        self.poller_sets = {}
        for poller_set in DBSession.query(model.PollerSet):
            self.poller_sets[poller_set.id] = [
                {'position': pr.position,
                 'poller': pr.poller.id,
                 'backend': pr.backend_id}
                for pr in poller_set.poller_rows]
        self.logger.debug(
            "Poller loaded %d Poller Sets.\n", len(self.poller_sets))

    def main_loop(self):
        """
        The main loop for the poller to do everything it needs to do.
        This will only exit if we have forced attributes and they are
        all polled.
        """
        self.logger.debug('Poller started, TID:%d', gettid())
        while True:
            now = datetime.datetime.now()
            polls_running = False
            if not self.forced_attributes and self.next_find_attribute < now:
                self.find_new_attributes()
                self.next_find_attribute = now +\
                    datetime.timedelta(seconds=self.find_attribute_interval)
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
            ping_jobs = self.ping_client.poll()
            timeout = 1.0
            if ping_jobs > 0:
                att_count -= ping_jobs
                timeout = 1.0

            if not self.zmq_core.poll(timeout):
                transaction.commit()
                return
            if self.end_thread:
                break
            if not polls_running and (self.polling_attributes == {}):
                # If there are no pollers, we can sleep until we need to
                # look for more attributes to poll
                if self.do_once or self.end_thread:
                    break
                transaction.commit()
                if self._sleep_until_next() is False:
                    return
        self.wait_for_workers()
        transaction.commit()

    def poller_callback(self, attribute_id, poller_value):
        """
        All real poller callback functions should call this method.
        It is how the real poller lets us know it has come back with
        something, including the value
        """
        try:
            patt = self.polling_attributes[attribute_id]
        except KeyError:
            self.logger.info(
                'A:%d - Poller called back but not in polling attributes',
                attribute_id)
            return
        try:
            poll_buffer = self.poller_buffer[attribute_id]
        except KeyError:
            self.logger.info(
                'A:%d -: Poller called back but no poller buffer',
                attribute_id)
            return
        try:
            pr_backend = self.backends[patt.poller_row['backend']]
        except KeyError:
            self.logger.info(
                'A:%d -: Poller called back but no backend found',
                attribute_id)
            return
        patt.stop_polling(patt.poller_row['position'], poller_value)
        patt.start_backend()
        backend_result = 'N/A'
        if poller_value is not None:
            if patt.poller.field != '':
                field_count = len(patt.poller.field.split(','))
                if field_count == 1:
                    poll_buffer[patt.poller.field] = poller_value
                else:
                    for ford, fkey in enumerate(
                            patt.poller.field.split(',')):
                        try:
                            poll_buffer[fkey] = poller_value[ford]
                        except KeyError:
                            self.logger.warning(
                                'A:%d - Field "%s" has no value from poller',
                                attribute_id, fkey)

            if pr_backend.enabled():
                attribute = model.Attribute.by_id(patt.id)
                backend_result = pr_backend.run(
                    patt.poller_row, attribute, poller_value)
        patt.stop_backend()
        self.logger.debug(
            "A:%d I:%d - %s:%s -> %s:%s (%d:%d)",
            patt.id, patt.poller_pos,
            patt.poller.display_name,
            self._poller_prettyprint(
                patt.poller_values[patt.poller_row['position']]),
            pr_backend.display_name, backend_result,
            patt.poller_times[patt.poller_row['position']],
            patt.backend_time)
        # Run the next poll row
        patt.in_poller = False

    def _poller_prettyprint(self, poller_value):
        """
        Print a nice output of the returned value from the poller for debugging
        """
        if poller_value is None:
            return 'None'
        max_len = 100
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
        for att_id, patt in self.polling_attributes.items():
            if patt.in_poller:
                continue
            if patt.poller_pos == 0:
                self.poller_buffer[att_id] = {}
            if patt.poller_pos not in patt.skip_rows:
                self._run_poller(patt)
            patt.poller_pos += 1

    def _run_poller(self, patt):
        """
        Run the actual poller
        """
        patt.start_polling()
        patt.poller_row = patt.get_poller_row()
        if patt.poller_row is None:
            #self.logger.error("A:%d - Poller could not get poller row %d:%d",
            #                  patt.id, patt.poller_set_id,
            #                  patt.poller_pos)
            self._finish_polling(patt)
            return
        try:
            patt.poller = self.pollers[patt.poller_row['poller']]
        except KeyError:
            self.logger.error("A:%d - Poller could not get poller %d",
                              patt.id, patt.poller_row['poller'])
            self._finish_polling(patt)
            return
        # Special speed-up for snmp fetch, get it all in one group
        # This does NOT work for SNMP v1, or this implementaiton anyhow
        if patt.poller.command == 'snmp_counter' and \
           not patt.host.ro_community.is_snmpv1():
            patt.skip_rows = self._multi_snmp_poll(patt)
            if patt.skip_rows != []:
                return
        if not patt.poller.run(patt.poller_row, self, patt,
                               self.poller_buffer[patt.id]):
            #run was successful
            self.logger.warn('A:%d - row %d Poller run failed', patt.id,
                             patt.poller_pos)
            self._finish_polling(patt)

    def _finish_polling(self, patt):
        """
        Complete all the finishing up that is required once a poller has
        run through its entire set of PollerRows
        """
        # Update all the relevant RRD files
        updated_rrds = []
        rrd_fields = model.DBSession.query(model.AttributeTypeRRD).filter(
            model.AttributeTypeRRD.attribute_type_id == patt.attribute_type_id)
        for rrd_field in rrd_fields:
            if rrd_field.name in self.poller_buffer[patt.id] and \
               self.poller_buffer[patt.id][rrd_field.name] is not None:
                updated_rrds.append('{0}:{1}'.format(
                    rrd_field.name,
                    rrd_field.update(
                        patt.id,
                        self.poller_buffer[patt.id][rrd_field.name],
                        rrd_client=self.rrd_client)))
        patt.update_poll_time()
        #DBSession.flush()
        transaction.commit()
        del (self.poller_buffer[patt.id])
        del (self.polling_attributes[patt.id])
        #self._run_backends(patt)
        self.logger.info(
            'A:%d - Polling complete - rrds: %s',
            patt.id, ', '.join(updated_rrds))

    def _run_backends(self, patt):
        """ Run all the backends for this polling attribute """
        attribute = model.Attribute.by_id(patt.id)
        for poller_row in patt.poller_set:
            start_time = time.time()
            if poller_row.backend.command == '':
                backend_result = ''
            else:
                backend_result = poller_row.run_backend(
                    attribute,
                    patt.poller_values[poller_row.position])
            self.logger.debug(
                "A:%d I:%d - %s:%s -> %s:%s (%d:%d)",
                patt.id, poller_row.position,
                poller_row.poller.display_name,
                self._poller_prettyprint(
                    patt.poller_values[poller_row.position]),
                poller_row.backend.display_name, backend_result,
                patt.poller_times[poller_row.position],
                (time.time() - start_time)*1000)
        attribute.update_poll_time()
        DBSession.flush()

    def _add_forced_attributes(self, attribute_ids=None, host_ids=None):
        """
        Add these attributes even if theyre not ready for polling.
        Method expects a list of attribute IDs or host_ids
        """
        if attribute_ids is not None:
            assert(type(attribute_ids) == list)
            for attribute in model.DBSession.query(model.Attribute).\
                    filter(model.Attribute.id.in_(attribute_ids)):
                self.attribute_add(attribute)
        if host_ids is not None:
            assert(type(host_ids) == list)
            for attribute in model.DBSession.query(model.Attribute).\
                    filter(model.Attribute.host_id.in_(host_ids)):
                self.attribute_add(attribute)

    def find_new_attributes(self):
        """
        Scan the attribute table and look for any attributes that need polling
        """
        hosts_down = {}
        self.logger.debug("Scanning attribute table to find new items to poll")
        next_poll_limit = datetime.datetime.now() + datetime.timedelta(
            seconds=POLLER_WINDOW_SECONDS)
        attributes = model.DBSession.query(model.Attribute).\
            join(model.Host).filter(and_(
                (model.Attribute.next_poll < next_poll_limit),
                (model.Attribute.poll_enabled == True))).\
            order_by(model.Attribute.next_poll)  # noqa
        if self.host_ids is not None:
            attributes = attributes.filter(
                model.Attribute.host_id.in_(self.host_ids))
        for attribute in attributes:
            # Skip if already polling
            if attribute.id in self.polling_attributes:
                continue

            # Skip if not main attribute and main atts down
            if not attribute.poll_priority:
                if attribute.host_id not in hosts_down:
                    hosts_down[attribute.host_id] =\
                        attribute.host.main_attributes_down()
                if hosts_down[attribute.host_id]:
                    self.logger.debug(
                        'H:%d A:%d not adding, main attribute(s) down.',
                        attribute.host_id, attribute.id)
                    attribute.update_poll_time()  # stop bothering the poller
                    continue
            self.attribute_add(attribute)

    def attribute_add(self, attribute):
        """
        Add the given attribute to the polled_attributes list the poller
        keeps. Also resets the pointers to first poller_set row
        """
        cache_att = CacheAttribute(attribute)
        try:
            cache_att.poller_set = self.poller_sets[attribute.poller_set_id]
        except KeyError:
            self.logger.error(
                "A:{} Cannot find PollerSet #{}".format(
                    attribute.id, attribute.poller_set_id))
            self.logger.error("IDs: {}".format(
                ",".join([str(k) for k in self.poller_sets.keys()])))
            raise
        self.polling_attributes[attribute.id] = cache_att

    def _multi_snmp_poll(self, patt):
        """
        This fast-forwards all SNMP queries into one request which should
        speed up the poller with SNMP heavy requests. The flip-side is that
        the strict poller order is not maintained
        """
        skip_rows = []
        #self.logger.debug("A#%d: multi_snmp start",patt.id)
        req = SNMPRequest(patt.host, patt.host.ro_community)
        for poller_row in patt.poller_set:
            if poller_row['position'] < patt.poller_row:
                continue
            try:
                pr_poller = self.pollers[poller_row['poller_id']]
            except KeyError:
                pass
            else:
                if pr_poller.command == 'snmp_counter':
                    oid = parse_oid(split_oid(
                        pr_poller.parsed_parameters(patt), patt.host))
                    if oid is not None:
                        data = {'pobj': self, 'poller_row': poller_row,
                                'attribute': patt}
                        req.add_oid(oid, cb_snmp_counter, **data)
                        skip_rows.append(poller_row['position'])
        if req.oids == []:
            return skip_rows
        patt.start_polling()
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
            self.logger.info(
                "Next polled attribute #%d at %s",
                next_attribute.id,
                next_attribute.next_poll.ctime())
            if self.next_find_attribute > next_attribute.next_poll:
                self.next_find_attribute = next_attribute.next_poll
            return self.sleep(self.next_find_attribute)

    def have_working_workers(self):
        return self.rrd_client.has_jobs()
