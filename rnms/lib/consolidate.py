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

# Import models for rnms
from rnms.model import DBSession
from rnms.model.logfile import Logfile, SyslogMessage

class Consolidator():
    """
    Consolidator process, may have some sub-processes under it
    """
    def consolidate(self):
        logfiles = DBSession.query(Logfile)
        for logfile in logfiles:
            if logfile.id == 1: # Magic 1 means internal database
                self.consolidate_syslog()
            else:
                self.consolidate_logfile(logfile)

    def consolidate_syslog(self):
        """
        Consolidates syslog messages from database
        """
        logging.info("LOGF: 1 (database)")
        line_count=0
        lines = DBSession.query(SyslogMessage).filter(SyslogMessage.consolidated==False)
        for line in lines:
            line_count += 1
            print line.message
        logging.info("LOGF(1): %d syslog messages processed" % line_count)

    def consolidate_logfile(self, logfile):

        logging.info("LOGF(%s): '%s'", logfile.id, logfile.pathname)
        line_count = 0
        if logfile.is_new() == False:
            logging.info("LOGF(%s): 0 messages processed ( No new lines).", logfile.id)
            return
        lfile = open(logfile.pathname, "r")
        lfile.seek(logfile.file_offset)
        for line in lfile:
            f = logfile.logmatchset.find(line)
            if f is not None:
                print(f)
            line_count += 1

        logging.info("LOGF(%s): %d messages processed" % (logfile.id, line_count))
        logfile.update(lfile.tell())

