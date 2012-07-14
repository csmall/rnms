#!/usr/bin/python
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012 Craig Small <csmall@enc.com.au>
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

from argparse import ArgumentParser
import sqlalchemy 
from paste.deploy import appconfig

from rnms.lib import logger
from rnms.config.environment import load_environment
from rnms import model


def load_config(filename):
    conf = appconfig('config:' + os.path.abspath(filename))
    load_environment(conf.global_conf, conf.local_conf)

def parse_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--conf_file', help="configuration to use", default='development.ini')
    parser.add_argument('--log', help="log level", default='WARNING')
    return parser.parse_args()

args = parse_args()
load_config(args.conf_file)
logger.init('SLA', args.log)

from rnms.lib.sla_analyzer import SLAanalyzer
slaa = SLAanalyzer()
slaa.analyze()
