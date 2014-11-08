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
from cliff.command import Command

from rnms.lib.snmptrapd import SNMPtrapd


class Trapd(Command):
    """ Start SNMP trap daemon """

    def get_parser(self, prog_name):
        parser = super(Trapd, self).get_parser(prog_name)
        parser.add_argument(
            '-P', '--port',
            action='store',
            dest='bind_port',
            type=int,
            help='UDP port to listen for SNMP traps (default 6162)',
            default=6162,
            metavar='PORT'
        )
        return parser

    def take_action(self, parsed_args):
        trapd = SNMPtrapd(bind_port=parsed_args.bind_port)
        trapd.run()
