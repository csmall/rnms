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
import errno

from cliff.command import Command

from tg import config


class StatusCommand(Command):
    """ Show the status of the rnms daemon """
    def take_action(self, parsed_args):
        pidfile = config['rnmsd_pid_file']
        try:
            pf = file(pidfile)
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            print 'Error reading pidfile'
            return

        if self._check_proc_alive(pid):
            daemon_status = 'running'
        else:
            daemon_status = 'died'

        print 'Daemon pid is {} and it is {}'.format(pid, daemon_status)

    def _check_proc_alive(self, pid):
        """ Returns true if the process is alive """
        try:
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                return False
        return True