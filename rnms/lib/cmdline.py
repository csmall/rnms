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
import os
import sys
import logging

from paste.script.command import Command
from paste.deploy import appconfig
from argparse import ArgumentParser

from rnms.config.environment import load_environment

LOG_FORMAT="%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s"
log = logging.getLogger(__name__)

class RnmsCommand(Command):
    """
    Base Object that provides a common interpretation of some of the command
    line arguments
    """
    summary = ''

    def __init__(self, name):
        super(RnmsCommand, self).__init__(name)
        self.parser = ArgumentParser(description=self.description)
        self.standard_options()

    def command(self):
        self._set_logging()
        pidfile = self._create_pid()
        try:
            self.real_command()
        finally:
            if pidfile:
                pidfile.close()
                os.remove(self.options.pidfile)

    def real_command(self):
        """ Command that is actually run by the object that inherits this
        class"""
        raise NotImplemented('real_command not implemented')

    def standard_options(self):
        """ Add the standard options """
        self.parser.add_argument(
            '-c', '--config',
            action='store',
            dest='config',
            help='Specify the config file to use for the command',
            default='production.ini',
        )
        self.parser.add_argument(
            '-d', '--debug',
            action='store_true',
            dest='log_debug',
            default=False,
            help='Turn on debugging',
        )
        self.parser.add_argument(
            '-p', '--pidfile',
            action='store',
            dest='pidfile',
            help='Location of pidfile',
            default='',
        )
        self.parser.add_argument(
            '-q', '--quiet',
            action='store_true',
            dest='log_quiet',
            default=False,
            help='Log critical messages only',
        )
        self.parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            dest='log_verbose',
            default=False,
            help='Increase verbosity of logging',
        )

    def run(self):
        self.options = self.parser.parse_args()
        self._get_config()
        result = self.command()
        if result is None:
            return self.return_code
        else:
            return result
    def _set_logging(self):
        logging_level = logging.WARNING
        if self.options.log_quiet == True:
            logging_level = logging.CRITICAL
        elif self.options.log_debug == True:
            logging_level = logging.DEBUG
        elif self.options.log_verbose == True:
            logging_level = logging.INFO
        logging.basicConfig(level=logging_level, format=LOG_FORMAT)

    def _create_pid(self):
        """ Create and check for PID file """
        if self.options.pidfile != '':
            if os.path.exists(self.options.pidfile):
                log.error('Exiting, pidfile %s exists',
                          self.options.pidfile)
                sys.exit(1)
                return
            pidfile = open(self.options.pidfile, 'w')
            pidfile.write(str(os.getpid()))
            pidfile.flush()
            return pidfile

    def _get_config(self):
        conf = appconfig('config:' + os.path.abspath(self.options.config))
        load_environment(conf.global_conf, conf.local_conf)


