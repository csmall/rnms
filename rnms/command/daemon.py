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
from cliff.command import Command
import transaction


from rnms.lib.daemon import RnmsDaemon


class DaemonCommand(Command):
    def get_parser(self, prog_name):
        parser = super(DaemonCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-D', '--no-daemon',
            action='store_true',
            dest='no_daemon',
            default=False,
            help='Do not detach and become a daemon',
        )
        parser.add_argument(
            '-p', '--pidfile',
            action='store',
            dest='pidfile',
            help='Location of pidfile',
            default='',
        )
        return parser

    def take_action(self, parsed_args):
        rnms = RnmsDaemon()
        rnms.run(parsed_args)
        transaction.commit()
