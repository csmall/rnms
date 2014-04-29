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
import os
import tempfile

from tg import config
from rnms import model
from rnms.lib.engine import RnmsEngine
from rnms.lib.gettid import gettid
from backup_model import CacheConfigHost
import plugins
"""
  Backup the configuration of the network element

  Unlike most other systems, this is single-threaded due to
  the limitations of most TFTP servers. The process uses this
  object and plugins for the specific transfer.

  plugin:start
  self.start_callback
  while plugin:transfer_wait is None:
     sleep
  plugin:cleanup
  self:cleanup_return
  """


class Backuper(RnmsEngine):
    _TFTP_PREFIX = 'config'
    _TFTP_SUFFIX = '.txt'
    NEED_CLIENTS = ('snmp',)
    host_ids = None
    current_host = None
    current_hid = None

    def __init__(self, host_ids=None, zmq_context=None):
        super(Backuper, self).__init__('backuper', zmq_context)
        self.host_ids = host_ids
        self.load_config()

    def load_config(self):
        """ Load the configuration from the Database """
        self.backup_methods = {}
        for m in model.DBSession.query(model.ConfigBackupMethod):
            if m.plugin_name == '':
                self.backup_methods[m.id] = None
            else:
                try:
                    backup_method = getattr(plugins, m.plugin_name)
                    self.backup_methods[m.id] = backup_method()
                except AttributeError:
                    raise ValueError(
                        "Plugin \"{}\" not found for Config Backup Method {}".
                        format(m.plugin_name, m.display_name))
        conditions = [(model.Host.id > 1)]
        if self.host_ids is not None:
            conditions.append(model.Host.id.in_(self.host_ids))
        self.hosts = {
            h.id: CacheConfigHost(h) for h in
            model.DBSession.query(model.Host).filter(*conditions)}

    def main_loop(self):
        """ Main loop for configuration transfers """
        self.logger.debug('Configuration backup started, TID:%s', gettid())
        self.logger.debug('Starting transfer for %d host(s).',
                          len(self.hosts))

        for hid, host in self.hosts.items():
            try:
                backup_method = self.backup_methods[host.method_id]
            except KeyError:
                self.logger.error(
                    'H:%d - Error finding method %s for host %s.',
                    hid, host.method_name, host.display_name)
                continue
            if backup_method is None:
                self.logger.debug(
                    'H:%d - Config transfer disabled for %s, skipping',
                    hid, host.display_name)
                continue
            self.logger.debug(
                'H:%d - Starting config transfer for %s using %s',
                hid, host.display_name, host.method_name)
            self.current_host = host
            host.backup_method = backup_method
            backup_method.start(self, host)
            while True:
                if not self._poll(host):
                    break

    def _poll(self, host):
        self.snmp_engine.poll()
        if not self.zmq_core.poll(2.0):
            return False
        if not host.poll(self):
            return False
        return not self.end_thread

    def start_callback(self, host, error, **kw):
        """
        The plugin:start() method returns here either when the starting
        of the transfer fails or it looks like it is successful
        error = None means we are successful so far
        """
        if error is not None:
            self.logger.error('H:%d - Error starting config copy %s',
                              host.id, str(error))
            self.current_host.done()
            return
        host.start_waiting(host.backup_method.wait_transfer, **kw)

    def transfer_callback(self, hid, error, **kw):
        """
        The plugin:transfer_wait calls this when the transfer is finished
        or it has failed
        """
        if error is not None:
            self.logger.error('H:%d - Error waiting for transfer %s',
                              hid, str(error))
            self.current_host.done()
            return
        self.current_host.done()

    def create_tftp_file(self, host):
        """ Creates an empty file for the TFTP server to use
        Requires the tftp_dir config entry
        """
        try:
            tftp_dir = config['tftp_dir']
        except KeyError:
            self.logger.error('H:%d - TFTP directory not defined in config',
                              host.id)
            return None
        if not os.path.isdir(tftp_dir):
            self.logger.error('H:%d - TFTP directory %s is not a directory.',
                              host.id, tftp_dir)
            return None
        tftp_file = tempfile.mkstemp(
            dir=tftp_dir,
            prefix=self._TFTP_PREFIX+str(host.id),
            suffix=self._TFTP_SUFFIX)
        os.close(tftp_file[0])
        os.chmod(tftp_file[1], 0777)
        return tftp_file[1]
