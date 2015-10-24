# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2014-2015 Craig Small <csmall@enc.com.au>
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
import logging.config as logging_config

from paste.deploy import appconfig
from cliff.app import App
from cliff.commandmanager import CommandManager

from rnms.config.environment import load_environment


class RnmsApp(App):
    log = logging.getLogger(__name__)

    def __init__(self):
        super(RnmsApp, self).__init__(
            description='RNMS app',
            version='0.1',
            command_manager=CommandManager('rnms.commands'),
        )

    def build_option_parser(self, description, version, kw=None):
        parser = super(RnmsApp, self).\
            build_option_parser(description, version, kw)
        parser.add_argument(
            '-c',
            action='store',
            dest='config',
            help='Specify the config file to use',
            default='production.ini',
            )
        return parser

    def initialize_app(self, argv):
        self._get_config()

    def prepare_to_run_command(self, cmd):
        pass
        # self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        # self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)

    def _config_logging(self, config_file):
        logging_config.fileConfig(
                config_file,
                dict(__file__=config_file,
                     here=os.path.dirname(config_file)))
        logging_level = {0: logging.WARNING,
                         1: logging.INFO,
                         2: logging.DEBUG,
                         }.get(self.options.verbose_level, logging.DEBUG)
        self.log.setLevel(logging_level)

    def _get_config(self):
        config_file = os.path.abspath(self.options.config)
        self._config_logging(config_file)
        try:
            conf = appconfig('config:' + config_file)
        except IOError as err:
            self.log.error(
                "Error setting up config file \"{}\": {}\n".format(
                    err.filename, err.strerror))
            sys.exit(1)
        load_environment(conf.global_conf, conf.local_conf)


def main(argv=sys.argv[1:]):
    myapp = RnmsApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
