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
import transaction

from rnms import model
from rnms.model import DBSession, Event
from rnms.model.logfile import Logfile, SyslogMessage

def consolidate_logfiles(logger):
    logfiles = DBSession.query(Logfile)
    for logfile in logfiles:
        if logfile.id == 1: # Magic 1 means internal database
            _cons_syslog(logger)
        else:
            _cons_logfile(logger, logfile)
    transaction.commit()

def _cons_syslog(logger):
    """
    Consolidates syslog messages from database
    """
    logger.info("LOGF: 1 (database)")
    line_count=0
    lines = DBSession.query(SyslogMessage).filter(SyslogMessage.consolidated==False)
    for line in lines:
        line_count += 1
    logger.info("LOGF(1): %d syslog messages processed" % line_count)

def _cons_logfile(logger, logfile):

    logger.info("LOGF(%s): '%s'", logfile.id, logfile.pathname)
    line_count = 0
    if logfile.is_new() == False:
        logger.info("LOGF(%s): 0 messages processed ( No new lines).", logfile.id)
        return
    lfile = open(logfile.pathname, "r")
    lfile.seek(logfile.file_offset)
    for line in lfile:
        find_data = logfile.logmatchset.find(line)
        if find_data is not None:
            new_event = Event(**find_data)
            DBSession.add(new_event)

        line_count += 1

    logger.info("LOGF(%s): %d messages processed" % (logfile.id, line_count))
    logfile.update(lfile.tell())
    lfile.close()
    DBSession.flush()




