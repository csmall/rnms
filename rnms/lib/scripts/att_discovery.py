# -*- coding: utf-8 -*-
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
import sys
import transaction

from rnms.lib.cmdline import RnmsCommand
from rnms.lib.att_discover import AttDiscover

class RnmsAttd(RnmsCommand):

    def real_command(self):
        host_ids = None
        if self.options.hosts is not None:
            host_ids = self.options.hosts.split(',')

        atype_ids = None
        if self.options.atypes is not None:
            atype_ids = self.options.atypes.split(',')

        autodiscovery = AttDiscover(force=self.options.force,
                                    print_only=self.options.print_only,
                                   do_once=True)
        autodiscovery.discover(limit_hosts=host_ids, limit_atypes=atype_ids)
        transaction.commit()
    
    def standard_options(self):
        super(RnmsAttd, self).standard_options()
        self.parser.add_argument(
            '-H', '--host',
            action='store',
            dest='hosts',
            type=str,
            help='Limit Attribute discovery to given host IDs',
            metavar='HID,...'
        )
        self.parser.add_argument(
            '-t', '--atype',
            action='store',
            dest='atypes',
            type=str,
            help='Limit Attribute discovery to given Attribute Type IDs',
            metavar='TID,...'
        )
        self.parser.add_argument(
            '-f', '--force',
            action='store_true',
            dest='force',
            help='Force Attribute Type discoveries',
        )
        self.parser.add_argument(
            '-n', '--dry-run',
            action='store_true',
            dest='print_only',
            help='Dry run - do not modify the database',
        )

def main():
    attd = RnmsAttd('att_disc')
    return attd.run()

if __name__ == '__main__':
    sys.exit(main())
