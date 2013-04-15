# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
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

from rnms.model import DBSession, SnmpTrap, TrapMatches

def consolidate_traps(logger):

    traps = DBSession.query(SnmpTrap).filter(SnmpTrap.processed == False)
    logger.info('%d SNMP Traps to process', traps.count())
    if traps.count() == 0:
        return

    for trap in traps:
        trap_matches = TrapMatches.by_oid(trap.trap_oid)
        if trap_matches is not None:
            for trap_match in trap_matches:
                (attribute, trap_value, error) = trap_match.run(trap.host, trap)
                if error is not None:
                    logger.warn('TrapMatch %s error: %s',trap_match.display_name, error)
                    continue
                if attribute is not None:
                    # We have matched to this trap
                    backend_result = trap_match.backend.run(None, attribute, trap_value)
                    logger.debug("A:%d %s:%s -> %s:%s", attribute.id, trap_match.display_name, str(trap_value )[:100], trap_match.backend.display_name, backend_result)
                    if trap_match.stop_if_match == True:
                        break

        trap.processed = True

    transaction.commit()
    
