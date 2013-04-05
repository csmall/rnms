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

from rnms import model


def consolidate_events(logger):
    """
    Scan all events that have not been previously checked and set alerts
    where required
    """
    events = model.DBSession.query(model.Event).filter(model.Event.processed == False)
    logger.info('%d Events to process', events.count())
    for event in events:
        if event.alarm_state.is_up():
            event.acknowledged = True
        
        if event.alarm_state is None or event.attribute is None:
            event.set_processed()
            continue

        if event.alarm_state.is_alert():
            process_event_alert(logger, event)
        else:
            down_alarm = model.Alarm.find_down(event.attribute, event.event_type)
            if event.alarm_state.is_downtesting():
                process_event_downtesting(logger, event, down_alarm)
            elif event.alarm_state.is_up():
                process_event_up(logger, event, down_alarm)
        event.set_processed()
    model.DBSession.flush()
    transaction.commit()

def process_event_alert(logger, event):
    """
    Process alert events.  These are unusual as they have a 
    fixed stop time and the stop_event is the start_event.
    Used mainly for Administration and SLA alarms that are
    only around for some time.
    Alert level events must have an attribute to raise an alarm.
    """
    logger.info("E:%d - ALERT Event - A:%d ET:%s", event.id, event.attribute.id, event.event_type.display_name)
    new_alarm = model.Alarm(event=event)
    model.DBSession.add(new_alarm)

def process_event_downtesting(logger, event, other_alarm):
    """
    Process down or testing events
    If there has been another alarm close it off and start a new one
    """
    logger.info("A:%d E:%d - DOWN/TESTING", event.attribute.id, event.id)
    if other_alarm is not None:
        other_alarm.set_stop(event, alarm_state=model.AlarmState.by_name('up'))
        #event.acknowledged=True
        other_alarm.start_event.acknowledged=True
    else:
        new_alarm = model.Alarm(event=event)
        model.DBSession.add(new_alarm)

def process_event_up(logger, event, other_alarm):
    event.acknowledged=True
    if other_alarm is not None:
        logger.info("A:%d E:%d - UP Event", event.attribute.id, event.id)
        other_alarm.set_stop(event)
        other_alarm.start_event.acknowledged=True


