# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2014 Craig Small <csmall@enc.com.au>
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
import re
import socket

from rnms.model import DBSession, Event, Host, Attribute, EventState
from rnms.model.logfile import Logfile, SyslogMessage, LogmatchSet

syslog_host_match = re.compile(r'\w{3} [ :0-9]{11} ([._a-z0-9-]+)\s+',
                               re.IGNORECASE)


class MatchRow(object):
    """ Static object for LogmatchSet rows """
    __copy_attrs__ = (
        'match_start', 'host_match', 'attribute_match', 'state_match',
        'event_type_id')
    fields = {}

    def __init__(self, db_row):
        self.match_sre = re.compile(db_row.match_text)
        for copy_attr in self.__copy_attrs__:
            self.setattr(copy_attr, db_row.getattr(copy_attr))
        for field in db_row.fields:
            self.fields[field.event_field_tag] = field.field_match

    def matched_host(self, match, line):
        """
        Return the matched host
        """
        syslog_match = syslog_host_match.match(line)
        if syslog_match is not None:
            address = syslog_match.group(1)

        if self.host_match is not None:
            try:
                groupid = int(self.host_match)
                address = match.group(groupid)
            except:
                pass
        if address is None:
            return None
        try:
            for addr in set([ai[4][0] for ai in
                             socket.getaddrinfo(address, 0)]):
                host = Host.by_address(addr)
                if host is not None:
                    return host
        except:
            pass
        return None

    def matched_attribute(self, match, host):
        """
        Return the matched attribute
        """
        if self.attribute_match is None:
            return None
        try:
            groupid = int(self.attribute_match)
        except ValueError:
            return None
        try:
            display_name = match.group(groupid)
        except IndexError:
            return None
        return Attribute.by_display_name(host, unicode(display_name))

    def matched_state(self, match):
        """
        Return the matched state
        """
        if self.state_match is None:
            return None
        try:
            return EventState.by_name(match.group(int(self.state_match)))
        except (ValueError, IndexError):
            return None

    def matched_fields(self, match):
        """
        Return a dictionary of tag:value for the fields for this LogmatchRow
        """
        mfields = {}
        for field in self.fields:
            try:
                groupid = int(field.field_match)
            except ValueError:
                mfields[field.event_field_tag] = field.field_match
            try:
                mfields[field.event_field_tag] = match.group(groupid)
            except IndexError:
                mfields[field.event_field_tag] = field.field_match
        return mfields

    def try_match(self, text):
        """
        Attempt to match this row against the given text.
        If we have a match then return a dictionary of items
        that can be used in an event, otherwise return None
        """
        if self.match_start:
            match = self.match_sre.match(text)
        else:
            match = self.match_sre.search(text)
        #match = re.search(row.match_text, text)
        if match is not None:  # we have a match!!
            host = self.matched_host(match, text)
            return dict(
                event_type=self.event_type,
                host=host,
                attribute=self.matched_attribute(match, host),
                alarm_state=self.matched_state(match),
                field_list=self.matched_fields(match),
                )


class LogfileConsolidator(object):
    match_sets = {}

    def __init__(self, logger):
        self.logger = logger
        self.load_config()

    def load_config(self):
        """ Load configuration for logfiles consolidation """
        self.match_sets = {}
        db_sets = DBSession.query(LogmatchSet)
        for db_set in db_sets:
            self.match_sets[db_set.id] = []
            for row in db_set.rows:
                self.match_sets[db_set.id].append(MatchRow(row))
        self.logger.debug(
            "Consolidator loaded %d match sets.\n", len(self.match_sets))

    def consolidate(self):
        """ Run the actual consolidation for logfiles """
        logfiles = DBSession.query(Logfile)
        for logfile in logfiles:
            if logfile.id == 1:  # Magic 1 means internal database
                self._cons_syslog(logfile)
            else:
                self._cons_logfile(logfile)
        transaction.commit()

    def _cons_syslog(self, logfile):
        """ Consolidates syslog messages from database """
        self.logger.info("LOGF: 1 (database)")
        try:
            match_set = self.match_sets[logfile.logmatchset_id]
        except KeyError:
            self.logger.error("LOGF(%s): MatchSet %d not found",
                              logfile.id, logfile.logmatchset_id)
            return
        lines = DBSession.query(SyslogMessage).\
            filter(SyslogMessage.consolidated == False)  # noqa
        self._run_matches(logfile.id, match_set, lines)

    def _cons_logfile(self, logfile):
        """ Consolidate the specified logfile """
        self.logger.info("LOGF(%s): '%s'", logfile.id, logfile.pathname)
        try:
            match_set = self.match_sets[logfile.logmatchset_id]
        except KeyError:
            self.logger.error("LOGF(%s): MatchSet %d not found",
                              logfile.id, logfile.logmatchset_id)
            return
        if not logfile.is_new():
            self.logger.info(
                "LOGF(%s): 0 messages processed ( No new lines).",
                logfile.id)
            return
        try:
            lfile = open(logfile.pathname, "r")
        except IOError as errmsg:
            self.logger.debug("LOGF(%s): Cannot open %s: %s", logfile.id,
                              logfile.pathname, errmsg)
            return
        lfile.seek(logfile.file_offset)
        self._run_matches(logfile.id, match_set, lfile)
        logfile.update(lfile.tell())
        lfile.close()

    def _run_matches(self, logfile_id, match_rows, loglines):
        """ Go over the  loglines looking for matches """
        line_count = 0
        for line in loglines:
            line_count += 1
            for row in match_rows:
                match_data = row.try_match(line)
                if match_data:
                    new_event = Event(**match_data)
                    DBSession.add(new_event)
        self.logger.info("LOGF(%s): %d messages processed",
                         logfile_id, line_count)
