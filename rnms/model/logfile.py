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
#
""" Logfile analysis objects"""

import datetime
import os
import transaction
import re 
import socket

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, PickleType, DateTime, Boolean, SmallInteger, String

#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, Attribute, AlarmState, Host
from rnms.lib.genericset import GenericSet

syslog_host_match = re.compile(r'\w{3} [ :0-9]{11} ([._[a-z0-9]-]+)\s+',re.IGNORECASE)

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
    file_mtime = Column(Integer, nullable=False, default=0) # stat st_mtime
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
        if os.access(self.pathname, os.R_OK) == False:
            #logging.warning("Cannot access file \"%s\" for reading." % self.pathname)
            return False
        if os.stat(self.pathname).st_mtime > self.file_mtime:
            return True
        return False

    def update(self, file_offset=None):
        """
        Update the mtime and (if given) the offset
        """
        self.file_mtime = os.stat(self.pathname).st_mtime
        if file_offset is not None:
            self.file_offset = file_offset
        transaction.commit()

class LogmatchSet(DeclarativeBase,GenericSet):
    __tablename__ = 'logmatch_sets'
    cached_matches = None
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(60), nullable=False, unique=True)
    logmatch_rows = relationship('LogmatchRow', order_by='LogmatchRow.position')
    #}

    def __init__(self, display_name=None):
        self.display_name = display_name
        self.rows = self.logmatch_rows

    def __repr__(self):
        return '<LogmatchSet name=%s rows=%d>' % (self.display_name,len(self.logmatch_rows))

    def insert(self, new_pos, new_row):
        new_row.logmatch_set = self
        GenericSet.insert(self,new_pos, new_row)

    def append(self, new_row):
        new_row.logmatch_set = self
        GenericSet.append(self,new_row)

    def prime_cache(self):
        """
        Put all database rows into cached_matches
        """
        self.cached_matches = [ row for row in self.logmatch_rows]

    def _match_get_fields(self, match, logfile_row, syslog_host):
        """
        Return a dictionary of fields that are extracted from the match
        """
        host=logfile_row.matched_host(match, syslog_host)
        return dict(event_type_id=logfile_row.event_type_id,
                host=host,
                attribute=logfile_row.matched_attribute(match,host),
                state = logfile_row.matched_state(match),
                fields = logfile_row.matched_fields(match)
                )

    def find(self, text, is_syslog=True):
        """
        Try to match "text" with any of the match rows
        returns None if not found otherwise a dictionary 
        """

        syslog_match = syslog_host_match.match(text)
        syslog_host = None
        if is_syslog and syslog_match is None:
            return False
        syslog_host = syslog_match.group(1)

        if self.cached_matches is None:
            self.prime_cache()

        for row in self.cached_matches:
            #print "trymatch: %s " % (row.match_text)
            if row.match_start:
                match = row.match_sre.match(text)
            else:
                match = row.match_sre.search(text)
            match = re.search(row.match_text, text)
            if match is not None: #we have a match!!
                print "match"
                return (self._match_get_fields(match, row, syslog_host))




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
    logmatch_set_id = Column(Integer, ForeignKey('logmatch_sets.id'), nullable=False)
    logmatch_set = relationship('LogmatchSet')
    position = Column(SmallInteger, nullable=False, default=1)
    match_text = Column(Unicode(255), nullable=False)
    match_sre = Column(PickleType)
    match_start = Column(Boolean, nullable=False, default=False)
    host_match = Column(Unicode(60))
    attribute_match = Column(Unicode(60))
    state_match = Column(Unicode(60))
    event_type_id = Column(Integer, ForeignKey('event_types.id'), nullable=False, default=0)
    fields = relationship('LogmatchField', backref='logmatch_row', cascade='all, delete, delete-orphan')

    def matched_host(self, match, syslog_host):
        """
        Return the matched host
        """
        if syslog_host is not None:
            address = syslog_host

        if self.host_match is not None:
            try:
                groupid=int(self.host_match)
                address = match.group(groupid)
            except:
                pass
        if address is None:
            return None
        try:
            for addr in set([ai[4][0] for ai in socket.getaddrinfo(address,0)]):
                host = Host.by_address(addr)
                if host is not None:
                    return host
        except:
            pass
        return None



    def matched_attribute(self, match,host):
        """
        Return the matched host
        """
        if self.attribute_match is None:
            return None
        try:
            groupid=int(self.attribute_match)
        except ValueError:
            return None

        try:
            display_name = match.group(groupid)
        except IndexError:
            return None
        return Attribute.by_display_name(host,display_name)

    def matched_state(self, match):
        """
        Return the matched state
        """
        if self.state_match is None:
            return None
        try:
            groupid=int(self.state_match)
        except ValueError:
            return None
        try:
            display_name = match.group(groupid)
        except IndexError:
            return None
        return AlarmState.by_name(display_name)

    def matched_fields(self,match):
        """
        Return a dictionary of tag:value for the fields for this LogmatchRow
        """
        mfields={}
        for field in self.fields:
            try:
                groupid=int(field.field_match)
            except ValueError:
                mfields[field.event_field_tag]=field.field_match
            try:
                mfields[field.event_field_tag]=match.group(groupid)
            except IndexError:
                mfields[field.event_field_tag]=field.field_match
        return mfields


class LogmatchField(DeclarativeBase):
    """
    Extra field matches for a LogmatchRow. The field_match follows same
    rules as _match fields found in LogmatchRow.
    The value is placed in the EventField that has the supplied tag
    """
    __tablename__ = 'logmatch_fields'

    #{ Columns
    logmatch_row_id = Column(Integer, ForeignKey('logmatch_rows.id'), primary_key=True, nullable=False)
    event_field_tag = Column(String(20),nullable=False, primary_key=True)
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
        return '<SyslogMessage message=%s>' % (self.message)


