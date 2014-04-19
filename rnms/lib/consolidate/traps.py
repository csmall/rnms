# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013-2014 Craig Small <csmall@enc.com.au>
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
from collections import defaultdict
import transaction

from rnms.model import DBSession, SnmpTrap, TrapMatch
from match_trap import MatchTrap


class TrapConsolidator(object):
    trap_matches = {}

    def __init__(self, logger):
        self.logger = logger
        self.load_config()

    def load_config(self):
        """ Load configuration from Database """
        self.trap_matches = defaultdict(list)
        trap_match_count = 0
        for trap_match in DBSession.query(TrapMatch).\
                order_by(TrapMatch.position):
            trap_match_count += 1
            self.trap_matches[trap_match.trap_oid].append(
                MatchTrap(trap_match))
        self.logger.debug("Trap Consolidator loaded %d trap rules.",
                          trap_match_count)

    def consolidate(self):
        """ Run the consolidator for SNMP traps """
        traps = DBSession.query(SnmpTrap).\
            filter(SnmpTrap.processed == False)  # noqa
        self.logger.info('%d SNMP Traps to process', traps.count())
        if traps.count() == 0:
            return

        for trap in traps:
            trap.processed = True
            try:
                trap_matches = self.trap_matches[trap.trap_oid]
            except KeyError:
                continue
            for trap_match in trap_matches:
                (attribute, trap_value, error) = \
                    trap_match.run(trap.host, trap)
                if error is not None:
                    self.logger.warn(
                        'TrapMatch error: %s',
                        error)
                    continue
                if attribute is not None:
                    # We have matched to this trap
                    backend_result = \
                        trap_match.backend.run(None, attribute, trap_value)
                    self.logger.debug(
                        "A:%d Trap:%s -> %s:%s",
                        attribute.id,
                        str(trap_value)[:100],
                        trap_match.backend.display_name,
                        backend_result)
                    if trap_match.stop_if_match is True:
                        break
        transaction.commit()
