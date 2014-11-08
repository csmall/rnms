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
import transaction
from cliff.command import Command

from rnms.lib.att_discover import AttDiscover


class AdiscCommand(Command):
    """ Discover attributes on hosts """
    def get_parser(self, prog_name):
        parser = super(AdiscCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-H', '--host',
            action='store',
            dest='hosts',
            type=str,
            help='Limit SLA analysis to given host IDs',
            metavar='HID,...'
            )
        parser.add_argument(
            '-t', '--atype',
            action='store',
            dest='atypes',
            type=str,
            help='Limit Attribute discovery to given Attribute Type IDs',
            metavar='TID,...'
            )
        parser.add_argument(
            '-f', '--force',
            action='store_true',
            dest='force',
            help='Force Attribute Type discoveries',
        )
        parser.add_argument(
            '-n', '--dry-run',
            action='store_true',
            dest='print_only',
            help='Dry run - do not modify the database',
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.hosts is not None:
            host_ids = parsed_args.hosts.split(',')
        else:
            host_ids = None
        if parsed_args.atypes is not None:
            atype_ids = parsed_args.atypes.split(',')
        else:
            atype_ids = None
        ad = AttDiscover(
            force=parsed_args.force,
            print_only=parsed_args.print_only,
            do_once=True)
        ad.discover(limit_hosts=host_ids, limit_atypes=atype_ids)
        transaction.commit()
