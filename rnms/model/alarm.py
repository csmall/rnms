# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2016 Craig Small <csmall@enc.com.au>
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

""" Alarm information """
import datetime

from sqlalchemy import ForeignKey, Column, and_, desc
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, DateTime, Boolean

from rnms.model import DeclarativeBase, DBSession
from rnms.lib.states import State


class Alarm(DeclarativeBase):
    """
    An alarm is some sort of alert on an attribute. They are created by
    an Event and share its EventState and EventType.
    If the EventType has a duration then the stop event is the same as the
    start Event and the stop time is after the duration expires.

    Alarms can also be stopped with an UP Event for the same EventType
    and Attribute.

    """
    __tablename__ = 'alarms'

    # { Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    event = relationship("Event",
                         primaryjoin="Event.id==Alarm.start_event_id")
    stop_event_id = Column(Integer, ForeignKey('events.id'))
    stop_event = relationship("Event",
                              primaryjoin="Event.id==Alarm.stop_event_id")
    stop_time = Column(DateTime)
    processed = Column(Boolean, nullable=False, default=False)
    check_stop_time = Column(Boolean, nullable=False, default=False)
    # }

    def __init__(self, event=None):
        if event is not None:
            self.event = event
            if event.event_type.alarm_duration > 0:
                self.stop_time = datetime.datetime.now() + datetime.timedelta(
                    minutes=event.event_type.alarm_duration)
                self.stop_event = event
                self.check_stop_time = True

    def __repr__(self):
        return '<Alarm {0} A:{1} T:{2}>'.format(
            self.id, self.event.attribute_id,
            self.event.created)

    def substitutes(self):
        """
        Returns a dictionary of parameters that are used for replacing
        information.
        """
        subs = {'attribute': '', 'client': '', 'host': '', 'state': ''}
        if self.attribute is not None:
            subs['attribute'] = self.attribute.display_name
            subs['client'] = self.attribute.user.display_name
            subs['interface-description'] = ' '.join(
                    [af.value for af in self.attribute.fields
                        if af.attribute_type.field.description])
            if self.attribute.host:
                subs['host'] = self.attribute.host.display_name
        return subs

    def set_stop(self, stop_event, event_state=None):
        """
        Set the stop attributes for this alarm.
        Requires the event that stopped the alarm and an optional
        new event_state to set the alarm to.
        Processed flag is cleared for the consolidator to trigger on
        an up alarm
        """
        if event_state is None:
            self.event_state = stop_event.event_state
        else:
            self.event_state = event_state
        self.stop_time = stop_event.created
        self.stop_event = stop_event
        self.check_stop_time = False
        self.processed = False
        self.event.acknowledged = True

    @classmethod
    def find_down(cls, attribute, event_type):
        """
        Find the first down or testing alarm of the given event_type
        for this attribute.
        """
        from rnms.model.event import EventState, Event
        if attribute is None or event_type is None:
            return None
        return DBSession.query(cls).join(Event, EventState).filter(and_(
            cls.event.attribute_id == attribute.id,
            cls.event.event_type_id == event_type.id,
            EventState.internal_state.in_([State.DOWN, State.TESTING]),
            )).order_by(desc(cls.id)).first()
