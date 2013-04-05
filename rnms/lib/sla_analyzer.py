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

# Import models for rnms
import logging
import datetime
import zmq
import transaction

from rnms.lib import zmqcore, zmqmessage
from rnms import model
from rnms.lib.engine import RnmsEngine

SLA_WINDOW_SECONDS = 10
SLA_INTERVAL_SECONDS = 180

class SLAanalyzer(RnmsEngine):
    """
    Analyze all of the SLA paramters on the attributes
    """
    attribute_ids=None
    host_ids=None
    forced_attributes = False
    next_find_attribute = datetime.datetime.min

    def __init__(self, attribute_ids=None, host_ids=None, zmq_context=None, do_once=True):
        super(SLAanalyzer, self).__init__('slaa', zmq_context)

        self.attribute_ids=attribute_ids
        self.host_ids = host_ids
        self.do_once = do_once

    def analyze(self):

        if self.do_once:
            next_sla_time = None
        else:
            next_sla_time = datetime.datetime.now()

        while True:
            attributes = self.find_new_attributes(next_sla_time)
            self.update_next_find_attribute()
            for attribute in attributes:
                if not self.zmq_core.poll(0.0):
                    return
                if self.end_thread:
                    return

                if attribute.is_down():
                    self.logger.debug('A%d: is DOWN, skipping',attribute.id)
                    continue
                self.logger.debug('A%d: START on %s',attribute.id, attribute.sla.display_name)
                attribute.sla.analyze(attribute, sla_logger=self.logger)
                attribute.update_sla_time()

            
            if self.do_once or self.end_thread == True:
                break
            transaction.commit()

            # otherwise we wait
            if self._sleep_until_next() == False:
                return
            next_sla_time = datetime.datetime.now() + datetime.timedelta(seconds=SLA_WINDOW_SECONDS)

    def find_new_attributes(self, next_sla_time):    
        """ Add new attributes that need to have their SLA analyzed """
        return model.Attribute.have_sla(next_sla_time, self.attribute_ids, self.host_ids)
    
    def _sleep_until_next(self):
        """
        Stay in this loop until we need to go into the main loop again.
        Returns False if we have broken out of the poll
        """
        next_attribute = model.Attribute.next_sla_analysis()
        if next_attribute is None:
            return self.sleep(self.next_find_attribute)
        else:
            self.logger.info("Next SLA Analysis #%d at %s", next_attribute.id, next_attribute.next_sla.ctime())
            if self.next_find_attribute > next_attribute.next_sla:
                self.next_find_attribute = next_attribute.next_sla
            return self.sleep(self.next_find_attribute)


            sleep_time = int((next_slaa_time - datetime.datetime.now()).total_seconds())
            self.logger.debug('Next SLA Analyzer in %d secs', sleep_time)
            while sleep_time > 0:
                if not self.zmq_core.poll(sleep_time):
                    return
                if self.end_thread:
                    return
                sleep_time = int((next_slaa_time - datetime.datetime.now()).total_seconds())
    def update_next_find_attribute(self):
        self.next_find_attribute = datetime.datetime.now() + datetime.timedelta(seconds=SLA_INTERVAL_SECONDS)
