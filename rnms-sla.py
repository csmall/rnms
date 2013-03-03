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
import logging
import sys

from argparse import ArgumentParser
import sqlalchemy 
from paste.deploy import appconfig

from rnms.config.environment import load_environment
from rnms import model
from rnms.lib.sla_analyzer import SLAanalyzer


def load_config(filename):
    conf = appconfig('config:' + os.path.abspath(filename))
    load_environment(conf.global_conf, conf.local_conf)

def parse_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--conf_file', help="configuration to use", default='development.ini')
    parser.add_argument('--log', help="log level", default='DEBUG')
    parser.add_argument('-a', '--atts', help='Attribute ids comma separated')
    parser.add_argument('-H', '--host', help='Only check attributes for these hosts', type=str, metavar='HOST,...' )
    return parser.parse_args()

args = parse_args()
load_config(args.conf_file)
logging.basicConfig(level=args.log)

if args.atts is None:
    attribute_ids=None
else:
    attribute_ids = args.atts.split(',')
if args.host is None:
    host_ids = None
else:
    host_ids = args.host.split(',')


slaa = SLAanalyzer(attribute_ids=attribute_ids,host_ids=host_ids)
slaa.analyze()
