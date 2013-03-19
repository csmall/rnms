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
import logging
import zmq

# Import models for rnms
from rnms.lib import zmqmessage, zmqcore
from rnms.model import DBSession, Event
from rnms.model.logfile import Logfile, SyslogMessage

class Consolidator():
    """
    Consolidator process, may have some sub-processes under it.
    A consolidator is something that takes a raw item, such as a syslog
    message, and turns it into an event possibly
    """
    consolidate_interval = 60

    logger = None
    zmq_context = None
    zmq_core = None
    control_socket = None
    do_once = True
    end_thread = False

    def __init__(self, zmq_context=None, do_once=True):
        self.do_once = do_once
        self.zmq_core = zmqcore.ZmqCore()

        if zmq_context is not None:
            self.zmq_context = zmq_context
            self.control_socket = zmqmessage.control_client(self.zmq_context)
            self.zmq_core.register_zmq(self.control_socket, self.control_callback)
        else:
            self.zmq_context = zmq.Context()
        self.logger = logging.getLogger('consol')

    def consolidate(self):

        while True:
            next_cons_time = datetime.datetime.now() + datetime.timedelta(seconds=self.consolidate_interval)
            logfiles = DBSession.query(Logfile)
            for logfile in logfiles:
                if not self.zmq_core.poll(0.0):
                    return
                if self.end_thread:
                    return

                if logfile.id == 1: # Magic 1 means internal database
                    self.consolidate_syslog()
                else:
                    self.consolidate_logfile(logfile)

            if self.do_once:
                return

            sleep_time = int((next_cons_time - datetime.datetime.now()).total_seconds())
            self.logger.debug("Next consolidation in %d secs", sleep_time)
            while sleep_time > 0:
                if not self.zmq_core.poll(sleep_time):
                    return
                if self.end_thread:
                    return
                sleep_time = int((next_cons_time - datetime.datetime.now()).total_seconds())

    def consolidate_syslog(self):
        """
        Consolidates syslog messages from database
        """
        self.logger.info("LOGF: 1 (database)")
        line_count=0
        lines = DBSession.query(SyslogMessage).filter(SyslogMessage.consolidated==False)
        for line in lines:
            line_count += 1
            print 'line msg',line.message
        self.logger.info("LOGF(1): %d syslog messages processed" % line_count)

    def consolidate_logfile(self, logfile):

        self.logger.info("LOGF(%s): '%s'", logfile.id, logfile.pathname)
        line_count = 0
        if logfile.is_new() == False:
            self.logger.info("LOGF(%s): 0 messages processed ( No new lines).", logfile.id)
            return
        lfile = open(logfile.pathname, "r")
        lfile.seek(logfile.file_offset)
        for line in lfile:
            find_data = logfile.logmatchset.find(line)
            if find_data is not None:
                new_event = Event(**find_data)
                DBSession.add(new_event)
                new_event.process()

            line_count += 1

        DBSession.flush()
        self.logger.info("LOGF(%s): %d messages processed" % (logfile.id, line_count))
        logfile.update(lfile.tell())

    def control_callback(self, socket):
        """
        Callback method for the control socket
        """
        frames = socket.recv_multipart()
        if frames[0] == zmqmessage.IPC_END:
            self.end_thread = True




