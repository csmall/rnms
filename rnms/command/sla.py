# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2014 Craig Small <csmall@enc.com.au>
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

from rnms.lib.sla_analyzer import SLAanalyzer


class Sla(Command):

    def get_parser(self, prog_name):
        parser = super(Sla, self).get_parser(prog_name)
        parser.add_argument(
            '-H', '--host',
            action='store',
            dest='hosts',
            type=str,
            help='Limit SLA analysis to given host IDs',
            metavar='HID,...'
            )
        parser.add_argument(
            '-a', '--attribute',
            action='store',
            dest='attributes',
            type=str,
            help='Limit SLA analysis to given Attribute IDs',
            metavar='AID,...'
            )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.hosts is not None:
            host_ids = parsed_args.hosts.split(',')
        else:
            host_ids = None
        if parsed_args.attributes is not None:
            att_ids = parsed_args.attributes.split(',')
        else:
            att_ids = None

        slaa = SLAanalyzer(attribute_ids=att_ids, host_ids=host_ids)
        slaa.analyze()
        transaction.commit()
