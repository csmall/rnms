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
from alarms import check_alarm_stop_time, check_alarm_triggers
from attributes import check_attribute_state
from events import consolidate_events
from logfiles import consolidate_logfiles
from traps import consolidate_traps

from rnms.lib.engine import RnmsEngine
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

    def _poll(self):
        if self.zmq_core.poll(0.0) == False:
            return False
        return self.end_thread == False
            
    def consolidate(self):

        while True:
            next_cons_time = datetime.datetime.now() + datetime.timedelta(seconds=self.consolidate_interval)
            consolidate_logfiles(self.logger)
            if self._poll() == False:
                return
            consolidate_traps(self.logger)
            if self._poll() == False:
                return
            changed_attributes = consolidate_events(self.logger)
            if self._poll() == False:
                return
            check_alarm_triggers(self.logger)
            changed_attributes.union(check_alarm_stop_time(self.logger))
            if self._poll() == False:
                return
            check_attribute_state(changed_attributes, self.logger)
            if self._poll() == False:
                return

            sleep_time = int((next_cons_time - datetime.datetime.now()).total_seconds())
            self.logger.debug("Next consolidation in %d secs", sleep_time)
            if self.sleep(next_cons_time) == False:
                return
