# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
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
import time

TRANSFER_TIMEOUT = 10  # 60*5
TRANSFER_POLL_INTERVAL = 2


class CacheConfigHost(object):
    __copy_attrs__ = (
        'id', 'display_name', 'mgmt_address', 'ro_community', 'rw_community')
    backup_object = None
    _timeout_time = 0
    _done = False
    _wait_func = None
    _wait_args = None
    _wait_time = 0

    def __init__(self, db_host):
        for copy_attr in self.__copy_attrs__:
            setattr(self, copy_attr, getattr(db_host, copy_attr))
        self.method_name = db_host.config_backup_method.display_name
        self.method_id = db_host.config_backup_method_id

    def set_start_time(self):
        self._timeout_time = time.time() + TRANSFER_TIMEOUT

    def poll(self, parent):
        if self._done:
            return False
        now = time.time()
        if self._timeout_time < now:
            parent.logger.warning(
                "H:%d - Transfer timed out.", self.id)
            return False
        if self._wait_func is not None and self._wait_time < now:
            self._wait_time = now + TRANSFER_POLL_INTERVAL
            return self._wait_func(parent, self, **self._wait_args)
        return True

    def start_waiting(self, wait_func, **kw):
        """
        Put this host into waiting which means running wait_func
        at regular intervals
        """
        self._wait_func = wait_func
        self._wait_args = kw

    def done(self):
        """ Called when transfer finished or failed """
        self._done = True
