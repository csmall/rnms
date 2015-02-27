# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2015 Craig Small <csmall@enc.com.au>
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
#
""" Logfile analysis objects"""

import datetime
import os
import re
import logging

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, PickleType, DateTime,\
    Boolean, SmallInteger, String

from rnms.model import DeclarativeBase
from rnms.lib.genericset import GenericSet

logger = logging.getLogger('rnms')
syslog_host_match = re.compile(r'\w{3} [ :0-9]{11} ([._a-z0-9-]+)\s+',
                               re.IGNORECASE)


class Logfile(DeclarativeBase):
    """
    Definition of a logfile that is regularly polled for new data.
    Row 0 is special as it uses the interal syslog table.
    """
    __tablename__ = 'log_files'

    #{ Columns

    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(60), nullable=False, unique=True)
    pathname = Column(Unicode(2000))
    polled = Column(DateTime, nullable=False, default=datetime.datetime.now)
    file_offset = Column(Integer, nullable=False, default=0)
    file_mtime = Column(Integer, nullable=False, default=0)  # stat st_mtime
    logmatchset_id = Column(Integer, ForeignKey('logmatch_sets.id'))
    logmatchset = relationship('LogmatchSet')
    #}

    def __init__(self, display_name=None, pathname=None):
        if display_name is not None:
            self.display_name = display_name
        if pathname is not None:
            self.pathname = pathname

    def is_new(self):
        """ Return a True/False depending on if the file has new items
        """
        if self.pathname is None:
            return False
        if self.file_offset == 0 or self.file_mtime == 0:
            return True
        if not os.access(self.pathname, os.R_OK):
            return False
        if os.stat(self.pathname).st_mtime > self.file_mtime:
            return True
        return False

    def update(self, file_offset=None):
        """
        Update the mtime and (if given) the offset
        """
        self.polled = datetime.datetime.now()
        if self.pathname != '':
            self.file_mtime = os.stat(self.pathname).st_mtime
        if file_offset is not None:
            self.file_offset = file_offset


class LogmatchSet(DeclarativeBase, GenericSet):
    __tablename__ = 'logmatch_sets'
    cached_matches = None

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(60), nullable=False, unique=True)
    logmatch_rows = relationship('LogmatchRow',
                                 order_by='LogmatchRow.position')
    #}

    def __init__(self, display_name=None):
        self.display_name = display_name
        self.rows = self.logmatch_rows

    def __repr__(self):
        return '<LogmatchSet name=%s rows=%d>'.format(
            self.display_name, len(self.logmatch_rows))

    def insert(self, new_pos, new_row):
        new_row.logmatch_set = self
        GenericSet.insert(self, new_pos, new_row)

    def append(self, new_row):
        new_row.logmatch_set = self
        GenericSet.append(self, new_row)


class LogmatchRow(DeclarativeBase):
    """
    A row within a LogmatchSet.
    This is used to scan a log file and do a regexp match on it.
    Each _text field is either a number which is the regexp group number
    or a text field. This text is placed into the created event.
    Arbitary fields are matched using the Logmatch fields
    The admin enters the match_text which is compiled into match_sre.
    The real matching is made from the compiled match_sre .
    """
    __tablename__ = 'logmatch_rows'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    logmatch_set_id = Column(Integer, ForeignKey('logmatch_sets.id'),
                             nullable=False)
    logmatch_set = relationship('LogmatchSet')
    position = Column(SmallInteger, nullable=False, default=1)
    match_text = Column(Unicode(255), nullable=False)
    match_sre = Column(PickleType)
    match_start = Column(Boolean, nullable=False, default=False)
    host_match = Column(Unicode(60))
    attribute_match = Column(Unicode(60))
    state_match = Column(Unicode(60))
    event_type_id = Column(Integer, ForeignKey('event_types.id'),
                           nullable=False, default=0)
    event_type = relationship('EventType')
    fields = relationship('LogmatchField', backref='logmatch_row',
                          cascade='all, delete, delete-orphan')


class LogmatchField(DeclarativeBase):
    """
    Extra field matches for a LogmatchRow. The field_match follows same
    rules as _match fields found in LogmatchRow.
    The value is placed in the EventField that has the supplied tag
    """
    __tablename__ = 'logmatch_fields'

    #{ Columns
    logmatch_row_id = Column(Integer, ForeignKey('logmatch_rows.id'),
                             primary_key=True, nullable=False)
    event_field_tag = Column(String(20), nullable=False, primary_key=True)
    field_match = Column(Unicode(150), nullable=False)
    #}


class SyslogMessage(DeclarativeBase):
    """
    A raw syslog message coming from a syslog daemon
    sent : time that the message was sent from the device
    received: time the message was recived by syslog server
    """

    __tablename__ = 'syslog_messages'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    facility = Column(Integer)
    level = Column(Integer)
    host = Column(Unicode(128))
    message = Column(Unicode(1024))
    consolidated = Column(Boolean, nullable=False, default=False)
    received = Column(DateTime, nullable=False, default=datetime.datetime.now)
    sent = Column(DateTime)
    #}

    def __init__(self, host=None, message=None):
        if host is not None:
            self.host = host
        if message is not None:
            self.message = message

    def __repr__(self):
        return '<SyslogMessage message=%s>'.format(self.message)
