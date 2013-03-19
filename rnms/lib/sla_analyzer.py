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

class SLAanalyzer():
    """
    Analyze all of the SLA paramters on the attributes
    """
    sla_analyzer_interval = 1800 # 30 minute SLA times
    attribute_ids=None
    host_ids=None

    logger = None
    zmq_context = None
    end_thread = False
    do_once = True

    def __init__(self, attribute_ids=None, host_ids=None, zmq_context=None, do_once=True):
        self.attribute_ids=attribute_ids
        self.host_ids = host_ids
        self.do_once = do_once
        self.zmq_core = zmqcore.ZmqCore()

        if zmq_context is not None:
            self.zmq_context = zmq_context
            self.control_socket = zmqmessage.control_client(self.zmq_context)
            self.zmq_core.register_zmq(self.control_socket, self.control_callback)
        else:
            self.zmq_context = zmq.Context()
        self.logger = logging.getLogger('slaa')

    def analyze(self):
        while True:
            next_slaa_time = datetime.datetime.now() + datetime.timedelta(seconds=self.sla_analyzer_interval)
            attributes = model.Attribute.have_sla(self.attribute_ids,self.host_ids)
            for attribute in attributes:
                if not self.zmq_core.poll(0.0):
                    return
                if self.end_thread:
                    return

                if attribute.is_down():
                    self.logger.debug('A%d: is DOWN, skipping',attribute.id)
                    continue
                self.logger.debug('A%d: START on %s',attribute.id, attribute.sla.display_name)
                attribute.sla.analyze(attribute)

            transaction.commit()
            
            if self.do_once:
                break

            # otherwise we wait
            sleep_time = int((next_slaa_time - datetime.datetime.now()).total_seconds())
            self.logger.debug('Next SLA Analyzer in %d secs', sleep_time)
            while sleep_time > 0:
                if not self.zmq_core.poll(sleep_time):
                    return
                if self.end_thread:
                    return
                sleep_time = int((next_slaa_time - datetime.datetime.now()).total_seconds())
    
    
    def control_callback(self, socket):
        """
        Callback method for the control socket
        """
        frames = socket.recv_multipart()
        if frames[0] == zmqmessage.IPC_END:
            self.end_thread = True

