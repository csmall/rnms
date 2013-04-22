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
import logging

from paste.deploy import appconfig

from rnms.config.environment import load_environment

LOG_FORMAT="%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s"

class BaseCmdLine(object):
    """
    Base Object that provides a common interpretation of some of the command
    line arguments
    """

    def parse_args(self, parser):
        """
        Add the common arguments to the command line
        """
        parser.add_argument("-c", "--conf_file", help="configuration to use", default="development.ini")
        parser.add_argument("-d", "--debug", action='store_true', help="turn on debugging")
        parser.add_argument("-q", "--quiet", action='store_true', help="critical messages only")
        parser.add_argument("-v", "--verbosity", action='store_true', help="verbose messages")

        self.args = parser.parse_args()

        self._set_logging()
        conf = appconfig('config:' + os.path.abspath(self.args.conf_file))
        load_environment(conf.global_conf, conf.local_conf)

    def _set_logging(self):
        logging_level = logging.WARNING
        if self.args.quiet == True:
            logging_level = logging.CRITICAL
        elif self.args.debug == True:
            logging_level = logging.DEBUG
        elif self.args.verbosity == True:
            logging_level = logging.INFO

        logging.basicConfig(level=logging_level, format=LOG_FORMAT)

