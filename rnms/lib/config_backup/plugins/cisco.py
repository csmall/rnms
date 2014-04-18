# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2014 Craig Small <csmall@enc.com.au>
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
# Parts of this file based upon the JFFNMS config engines which are
# Copyright 2002-2005 Javier Szyszlican <javier@szysz.com>

from base import ConfigBackupPlugin
from rnms.lib.snmp import SNMPSetRequest
from random import randint

CC_COPY_ENTRY = (1, 3, 6, 1, 4, 1, 9, 9, 96, 1, 1, 1, 1)
KEY_PROTO = 2
KEY_SOURCE_FILETYPE = 3
KEY_DEST_FILETYPE = 4
KEY_SERVER_ADDR = 5
KEY_DEST_FILENAME = 6
KEY_ROW_STATUS = 14

# Values
VAL_DESTROY = 6
VAL_CREATEANDGO = 4
VAL_TFTP = 1
VAL_RUNNING = 4
VAL_NETWORK = 1

STATUS_WAITING = 1
STATUS_RUNNING = 2
STATUS_SUCCESSFUL = 3
STATUS_FAILED = 4


class cisco_cc(ConfigBackupPlugin):
    """ Copy the configuration file to the TFTP server using the Cisco
    CISCO-CONFIG-COPY-MIB
    w
    Reference:
    http://www.cisco.com/c/en/us/support/docs/ip/
     simple-network-management-protocol-snmp/15217-copy-configs-snmp.html
    """
    def start(self, parent, host):
        copy_id = randint(1, 9999)
        host.set_start_time()
        req = SNMPSetRequest(
            host, host.rw_community, self.cb_destroy,
            copy_id=copy_id, parent=parent)
        req.set_int(CC_COPY_ENTRY+(KEY_ROW_STATUS, copy_id), VAL_DESTROY)
        parent.snmp_engine.set(req)
        return True

    def cb_destroy(self, value, error, **kw):
        if error is not None:
            kw['parent'].parent_callback(kw['host'].id, False)
            return
        kw['parent'].logger.debug('H:%d - Destroy function ok', kw['host'].id)
        req = SNMPSetRequest(
            kw['host'], kw['host'].rw_community, self.cb_start,
            copy_id=kw['copy_id'], parent=kw['parent'])
        req.set_int(CC_COPY_ENTRY+(KEY_PROTO, kw['copy_id']), VAL_TFTP)
        req.set_int(CC_COPY_ENTRY+(KEY_SOURCE_FILETYPE, kw['copy_id']),
                    VAL_RUNNING)
        req.set_int(CC_COPY_ENTRY+(KEY_DEST_FILETYPE, kw['copy_id']),
                    VAL_NETWORK)
        req.set_ipaddr(CC_COPY_ENTRY+(KEY_SERVER_ADDR, kw['copy_id']),
                       '172.16.242.1')
        req.set_str(CC_COPY_ENTRY+(KEY_DEST_FILENAME, kw['copy_id']), 'foo')
        req.set_int(CC_COPY_ENTRY+(KEY_ROW_STATUS, kw['copy_id']),
                    VAL_CREATEANDGO)
        if kw['parent'].snmp_engine.set(req) is False:
            kw['parent'].start_callback(
                kw['host'],
                'Error sending SNMP set')

    def cb_start(self, value, error, **kw):
        if error is not None:
            kw['parent'].start_callback(kw['host'], error)
            return
        kw['parent'].logger.debug('H:%d - Transfer command sent',
                                  kw['host'].id)
        kw['parent'].snmp_engine.get_int(
            kw['host'],
            CC_COPY_ENTRY+(KEY_ROW_STATUS, kw['copy_id']),
            self.cb_start2,
            copy_id=kw['copy_id'], parent=kw['parent'])

    def cb_start2(self, value, error, **kw):
        if error is not None:
            kw['parent'].start_callback(kw['host'], error)
            return
        if value == STATUS_FAILED:
            kw['parent'].start_callback(kw['host'], 'transfer failed')
            return
        kw['parent'].start_callback(kw['host'], None, copy_id=kw['copy_id'])

    def wait_transfer(self, parent, host, **kw):
        """ Start off the polling for the transfer """
        return parent.snmp_engine.get_int(
            host,
            CC_COPY_ENTRY+(KEY_ROW_STATUS, kw['copy_id']),
            self.cb_wait_transfer,
            copy_id=kw['copy_id'], parent=parent)

    def cb_wait_transfer(self, value, error, **kw):
        if error is not None:
            kw['parent'].transfer_callback(kw['host'], error)
            return
        if value == STATUS_FAILED:
            kw['parent'].transfer_callback(kw['host'], 'transfer failed')
            return
        if value == STATUS_SUCCESSFUL:
            kw['parent'].transfer_callback(
                kw['host'], None, copy_id=kw['copy_id'])


class cisco_sys(ConfigBackupPlugin):
    pass  # FIXME


class cisco_catos(ConfigBackupPlugin):
    pass  # FIXME
