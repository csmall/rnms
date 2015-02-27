# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
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

from rnms.model import DBSession, Event


def process_events(logger):
    """
    Scan all events that have not been previously checked and set alerts
    where required.
    Returns a set of changed attributes
    """
    changed_attributes = set()
    events = DBSession.query(Event).filter(Event.processed == False)
    logger.info('%d Events to process', events.count())
    for event in events:
        if event.event_state is None or event.attribute is None:
            event.set_processed()
            continue


        if event.event_state.is_up():
            event.acknowledged = True

        changed_attributes.add(event.attribute_id)

        if event.event_state.is_alert() == False:
            down_event = Event.find_down(event.attribute_id,
                                         event.event_type_id,
                                        event.id)
            if event.event_state.is_downtesting():
                process_event_downtesting(logger, event, down_event)
            elif event.event_state.is_up():
                process_event_up(logger, event, down_event)
        event.set_processed()
    transaction.commit()
    return changed_attributes

def process_event_downtesting(logger, event, other_event):
    """
    Process down or testing events.  If there has been an alarmed event
    for this, then we don't do anything with this one.
    """
    if other_event is not None:
        logger.info("A:%d E:%d - DOWN/TESTING", event.attribute_id, event.id)
        event.triggered = True
        event.alarmed = False
        if event.check_stop_time:
            # Extend the stop time
            other_event.stop_time = event.stop_time
            other_event.check_stop_time = True
            event.check_stop_time = False

def process_event_up(logger, event, other_event):
    event.acknowledged=True
    if other_event is not None:
        logger.info("A:%d E:%d - UP Event", event.attribute_id, event.id)
        other_event.set_stop(event)


def check_event_stop_time(logger):
    """
    Run through all the events that have check_stop_time set to
    see if we have reached the time to close off the event.
    This generally clears a SLA alarm on an Attribure after it has
    expired, for example.

    Returns a set of Attribute IDs that have had a status change
    """
    changed_attributes = set()
    events = Event.check_time_events()
    if events is not None:
        for event in events:
            event.check_stop_time = False
            changed_attributes.add(event.attribute_id)
    return changed_attributes

