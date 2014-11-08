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
import os
import transaction

from cliff.command import Command

from rnms.lib.jffnms_config import JffnmsConfig
from rnms.lib.jffnms_import import JffnmsImporter


class JffnmsImport(Command):
    """ Import database from a JFFNMS instance """
    def get_parser(self, prog_name):
        parser = super(JffnmsImport, self).get_parser(prog_name)
        parser.add_argument(
            '-n', '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Do not insert records into database',
        )
        parser.add_argument(
            '--jffnms-conf',
            action='store',
            dest='jffnms_conf',
            help='Directory where JFFNMS configuration file is',
            default='/etc/jffnms/',
            metavar='DIR'
        )
        return parser

    def take_action(self, parsed_args):
        if not os.path.isdir(parsed_args.jffnms_conf):
            raise RuntimeError(
                "\"{}\" is not a directory, check your --jffnms_conf setting".
                format(parsed_args.jffnms_conf))

        jconf = JffnmsConfig()
        jconf.parse(parsed_args.jffnms_conf)
        jimport = JffnmsImporter(self, jconf)

        jimport.do_delete()
        if not parsed_args.dry_run:
            transaction.commit()
        jimport.import_all()
        if not parsed_args.dry_run:
            transaction.commit()
        jimport.print_conf_shell(jconf)
