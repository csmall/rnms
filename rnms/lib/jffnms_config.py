# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011-2014 Craig Small <csmall@enc.com.au>
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
#
""" JFFNMS configuration file """

import re
import sys

CONFIG_LINE_RE = re.compile('([a-z_]+)\s+=\s+(\S.+)', re.IGNORECASE)
DEFAULT_LINE_RE = re.compile('([a-z_]+):([a-z]+)\s+=\s+(\S.+)', re.IGNORECASE)


class JffnmsConfig(object):
    """
    Configuration object for JFFNMS configurations.
    The object on creation needs to be given config_dir where the
    JFFNMS configuration files live.
    """
    def __init__(self):
        self.config_values = {}

    def parse(self, config_dir):
        self._parse_default_file(config_dir)
        self._parse_config_file(config_dir)

    def _parse_default_file(self, config_dir):
        try:
            with open(config_dir + '/jffnms.conf.defaults', 'rt') as default_file:
                skip_config = None
                for line in default_file:
                    result = DEFAULT_LINE_RE.match(line)
                    if result:
                        if len(result.groups()) != 3:
                            next
                        (conf_key, conf_type, conf_value) = result.groups()
                        if skip_config is not None and skip_config == conf_key:
                            next
                        if conf_type in ('description', 'values'):
                            next
                        elif conf_type == 'type':
                            if conf_value == 'phpmodule':
                                skip_config = conf_key
                            else:
                                skip_config = None
                            next
                        elif conf_type == 'default':
                            self.config_values[conf_key] = conf_value.rstrip()
        except IOError as err:
            sys.stderr.write(
                "Unable to open default JFFNMS config file \"{}\": {}\n".
                format(err.filename, err.strerror))
            sys.exit(1)

    def _parse_config_file(self, config_dir):
        config_file = file(config_dir + '/jffnms.conf','r')
        for line in config_file:
            result = CONFIG_LINE_RE.match(line)
            if result:
                self.config_values[result.group(1)] = result.group(2).strip()
        config_file.close()

    def get(self, key):
        return self.config_values[key]

