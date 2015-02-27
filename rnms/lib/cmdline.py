# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2013-2015 Craig Small <csmall@enc.com.au>
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
import signal
from logging.config import fileConfig

from paste.script.command import Command
from paste.deploy import appconfig
from argparse import ArgumentParser

from rnms.config.environment import load_environment

LOG_FORMAT = "%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s"
log = logging.getLogger(__name__)


class RnmsCommand(Command):
    """
    Base Object that provides a common interpretation of some of the command
    line arguments
    """
    summary = ''
    __sighup_handlers = []

    def __init__(self, name):
        super(RnmsCommand, self).__init__(name)
        self.parser = ArgumentParser(description=self.description)
        self.standard_options()

    def command(self):
        self._set_logging()
        self.create_pidfile()
        try:
            self.real_command()
        finally:
            self.del_pidfile()

    def daemonize(self):
        """ Daemonize the process """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.syserr.write("fork #1 failed: {} ({})\n".
                             format(e.errno, e.strerror))

        #  Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from the second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: {} ({})\n".format(
                e.errno, e.strerror))

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file("/dev/null", "r")
        so = file("/dev/null", "a+")
        se = file("/dev/null", "a+")
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

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
            '-D', '--no-daemon',
            action='store_true',
            dest='no_daemon',
            default=False,
            help='Do not detach and become a daemon',
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
        signal.signal(signal.SIGHUP, self._sighup_handler)
        result = self.command()
        if result is None:
            return self.return_code
        else:
            return result

    def _set_logging(self):
        logging_level = logging.WARNING
        if self.options.log_quiet:
            logging_level = logging.CRITICAL
        elif self.options.log_debug:
            logging_level = logging.DEBUG
        elif self.options.log_verbose:
            logging_level = logging.INFO
        logging.basicConfig(level=logging_level, format=LOG_FORMAT)

    def create_pidfile(self):
        """ Create and check for PID file """
        if self.options.pidfile == '':
            return

        try:
            pf = file(self.options.pidfile)
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            log.error('Exiting, pidfile {} already exists for process {}',
                      self.options.pidfile, pid)
            sys.exit(1)
            return

        try:
            pf = open(self.options.pidfile, 'w+')
            pf.write("{}\n".format(os.getpid()))
        except IOError as err:
            log.error("Unable to write pidfile {}: {}\n".format(
                self.options.pidfile, err))

    def del_pidfile(self):
        """ Delete our pidfile """
        if self.options.pidfile != "":
            os.remove(self.options.pidfile)

    def _get_config(self):
        config_file = os.path.abspath(self.options.config)
        try:
            conf = appconfig('config:' + config_file)
        except IOError as err:
            sys.stderr.write(
                "Error setting up config file \"{}\": {}\n".format(
                    err.filename, err.strerror))
            sys.exit(1)
        load_environment(conf.global_conf, conf.local_conf)
        fileConfig(config_file, dict(__file__=config_file,
                                     here=os.path.dirname(config_file)))

    # Signal handling
    def _sighup_handler(self, sig_num, stack_frame):
        """ Run when device gets a HUP """
        self.logger.debug("Received HUP\n")
        for hdl in self.__sighup_handlers:
            hdl()

    def add_sighup_handler(self, handler):
        """ Add another signal HUP handler """
        self.__sighup_handlers.append(handler)
