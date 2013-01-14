#!/usr/bin/python
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
from argparse import ArgumentParser
import transaction

from paste.deploy import appconfig
from rnms.config.environment import load_environment

from rnms.lib.info import RnmsInfo

def load_config(filename):
    conf = appconfig('config:' + os.path.abspath(filename))
    load_environment(conf.global_conf, conf.local_conf)

def parse_args():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--conf_file', help="configuration to use", default='development.ini')
    parser.add_argument('qtype', type=str, choices=('attribute', 'host', 'pollerset'), help='Choose attributei,host or pollerset', metavar='<query_type>')
    parser.add_argument('ids', metavar='ID ID...', type=int, nargs='+')
    return parser.parse_args()

args = parse_args()
load_config(args.conf_file)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("rnms")


rnms_info = RnmsInfo()
if args.qtype == 'host':
    rnms_info.host_info(args.ids)
elif args.qtype == 'attribute':
    rnms_info.attribute_info(args.ids)
elif args.qtype == 'pollerset':
    rnms_info.pollerset_info(args.ids)
