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
import os
import signal

from cliff.command import Command

from tg import config
from rnms.lib.pid import check_proc_alive


class StopCommand(Command):
    """ Stop the RNMS backend daemon """
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        print('hi')
        pidfile = config['rnmsd_pid_file']
        try:
            pf = file(pidfile)
            pid = int(pf.read().strip())
            pf.close()
        except IOError as e:
            self.log.debug(
                    "PID file \"%s\" not found: %s",
                    pidfile, e.message)
            return

        print(pid)
        if check_proc_alive(pid):
            self.log.debug('Sending process {} SIGTERM'.format(pid))
            os.kill(pid, signal.SIGTERM)
            print('stoping?')
