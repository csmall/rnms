# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2014-2016 Craig Small <csmall@enc.com.au>
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
import logging
import zmq

from cliff.command import Command

from tg import config
from rnms.lib.pid import check_proc_alive
from rnms.lib import zmqmessage


class StatusCommand(Command):
    """ Show the status of the rnms daemon """
    log = logging.getLogger(__name__)
    zmq_context = None
    info_socket = None

    def take_action(self, parsed_args):
        pidfile = config['rnmsd_pid_file']
        try:
            pf = file(pidfile)
            pid = int(pf.read().strip())
            pf.close()
        except IOError as e:
            self.log.debug(
                    "PID file \"%s\" not found: %s",
                    pidfile, e.message)
            print 'Rnmsd is NOT running - no pidfile found'
            return

        if check_proc_alive(pid):
            print 'Rnms is running - pid {}'.format(pid)
            self._create_info_socket()
        else:
            print 'Rnms is NOT running - stale pid {}'.format(pid)

    def _create_info_socket(self):
        context = zmq.Context()
        socket = zmqmessage.info_client(context)
        socket.linger = 1000
        thread_info = zmqmessage.get_info(socket)
        if thread_info is None:
            print('Problem getting thread information')
        else:
            print('{} threads running:\n'.
                  format(thread_info['thread_count']))
            for task in thread_info['tasks']:
                print(' {} - {}'.format(
                    task['name'],
                    'Running' if task['alive'] else ['Dead']))
