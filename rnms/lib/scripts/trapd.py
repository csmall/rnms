
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

from rnms import model
from rnms.lib.cmdline import RnmsCommand
from rnms.lib.snmptrapd import SNMPtrapd

class RnmsTrapd(RnmsCommand):
    """
    Provides information about the various objects in rnms
    """

    def real_command(self):
        trapd = SNMPtrapd(bind_port=self.options.bind_port)
        trapd.run()
    
    def standard_options(self):
        super(RnmsTrapd, self).standard_options()
        self.parser.add_argument(
            '-P', '--port',
            action='store',
            dest='bind_port',
            type=int,
            help='UDP port to listen for SNMP traps (default 6162)',
            default=6162,
            metavar='PORT'
        )

def main():
    td = RnmsTrapd('trapd')
    return td.run()

if __name__ == '__main__':
    sys.exit(main())
