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
import logging

from rnms.lib.daemon import RnmsDaemon


class StartCommand(Command):
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(StartCommand, self).get_parser(prog_name)
        parser.add_argument(
            '-f', '--foreground',
            action='store_true',
            dest='foreground',
            default=False,
            help='Remain in the foreground and don\'t fork',
        )
        return parser

    def take_action(self, parsed_args):
        daemon = RnmsDaemon(self.log)
        daemon.run(parsed_args)
