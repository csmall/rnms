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
from rnms import model

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

    def consolidate_events(self):
        """
        Process all events looking for up/down event types against
        attributes
        """
        new_events = DBSession.query(model.Events).filter(Events.analyzed==False).filter(Events.attribute.check_status==True).filter(Events.type.generate_alarm==True)
        logging.info("EVENTS: %d events to process." % new_events.count())
        for new_event in new_events:
            #FIXME check type and alarm up type???
            logging.info("E %d:= @%s - state: %s - att: %s - type: %s",
                    new_event.id, new_event.alarm_state.display_name,
                    new_event.attribute.display_name,
                    new_event.event_type.display_name)

            if new_event.alarm_state.is_alert():
                process_event_alert(new_event)

            other_alarm = model.Alarm.find_down(attribute,event_type)
            if new_event.alarm_state.is_downtesting():
                process_event_downtesting(new_event, other_alarm)
            elif new_event.alarm_state.is_up():
                process_event_up(new_event, other_alarm)
            new_event.analyzed = True
            # FIXME triggers


def process_event_alert(event):
    """
    Process alert events.  These are unusual as they have a 
    fixed stop time and the stop_event is the start_event.
    Used mainly for Administration and SLA alarms that are
    only around for some time.
    """
    logging.info("E %d := ALERT Attribute %d",
            event.id, event.attribute.display_name)

    new_alarm = model.Alarm(event=event)
    new_alarm.stop_time = datetime.datetime.now() + datetime.timedelta(minutes=(event.event_type.alarm_duration+30))
    new_alarm.stop_event = event
    DBSession.add(new_alarm)

def process_event_downtesting(event, other_alarm):
    """
    Process down or testing events
    """
    if other_alarm is not None:
        other_alarm.set_stop(event, alarm_state=model.AlarmState.by_name('up'))
        event.acknowledged=True
        other_alarm.start_event.acknowledged=True

    logging.info("E %d:= DOWN/TESTING Interface %s",
        event.id, event.attribute.display_name)

    new_alarm = model.Alarm(event)
    DBSession.add(new_alarm)

    


