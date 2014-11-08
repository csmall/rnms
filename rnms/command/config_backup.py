# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013-2014 Craig Small <csmall@enc.com.au>
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
"""
Configuration backup script
  This script will backup the various supported devices
  and store updated configurations in the database
"""
import transaction
from cliff.command import Command

from rnms.lib.config_backup import Backuper


class CbackupCommand(Command):
    """ Backup hosts configuration """
    def get_parser(self, prog_name):
        parser = super(CbackupCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-H', '--host',
            action='store',
            dest='hosts',
            type=str,
            help='Backup these hosts only',
            metavar='HID,...'
            )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.hosts is not None:
            host_ids = parsed_args.hosts.split(',')
        else:
            host_ids = None
        backuper = Backuper(host_ids=host_ids)
        backuper.main_loop()
        transaction.commit()
