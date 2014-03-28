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

# Import models for rnms
#from alarms import check_alarm_stop_time, check_alarm_triggers
from attributes import check_attribute_state, check_all_attributes_state
from events import process_events, check_event_stop_time
from logfiles import LogfileConsolidator
from traps import TrapConsolidator

from rnms.lib.engine import RnmsEngine
from rnms.lib.gettid import gettid


class Consolidator(RnmsEngine):
    """
    Consolidator process, may have some sub-processes under it.
    A consolidator is something that takes a raw item, such as a syslog
    message, and turns it into an event possibly
    """
    consolidate_interval = 60

    do_once = True

    def __init__(self, zmq_context=None, do_once=True):
        self.do_once = do_once
        super(Consolidator, self).__init__('cons', zmq_context)
        self.logfile_consolidator = LogfileConsolidator(self.logger)
        self.trap_consolidator = TrapConsolidator(self.logger)

    def _poll(self):
        if not self.zmq_core.poll(0.0):
            return False
        return not self.end_thread

    def sighup_handler(self):
        """ Handle HUP signal by reloading config """
        self.logfile_consolidator.load_config()
        self.trap_consolidator.load_config()

    def consolidate(self):
        self.logger.debug('Consolidator started TID:%d', gettid())
        if not self.do_once:
            check_all_attributes_state(self.logger)

        while True:
            next_cons_time = datetime.datetime.now() +\
                datetime.timedelta(seconds=self.consolidate_interval)
            self.logfile_consolidator.consolidate()
            if not self._poll():
                return
            self.trap_consolidator.consolidate()
            if not self._poll():
                return
            changed_attributes = process_events(self.logger)
            if not self._poll():
                return
            changed_attributes.union(check_event_stop_time(self.logger))
            if not self._poll():
                return
            check_attribute_state(changed_attributes, self.logger)
            if not self._poll():
                return

            sleep_time = int((next_cons_time -
                              datetime.datetime.now()).total_seconds())
            self.logger.debug("Next consolidation in %d secs", sleep_time)
            if self.do_once:
                return
            if not self.sleep(next_cons_time):
                return
