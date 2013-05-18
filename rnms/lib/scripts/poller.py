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
from rnms.lib.poller import Poller

class RnmsPollCmd(RnmsCommand):

    def real_command(self):
        host_ids = None
        if self.options.hosts is not None:
            host_ids = self.options.hosts.split(',')

        att_ids = None
        if self.options.attributes is not None:
            att_ids = self.options.attributes.split(',')

        poller = Poller(attribute_ids=att_ids,host_ids=host_ids)
        poller.main_loop()
        transaction.commit()
    
    def standard_options(self):
        super(RnmsPollCmd, self).standard_options()
        self.parser.add_argument(
            '-H', '--host',
            action='store',
            dest='hosts',
            type=str,
            help='Limit polling to given host IDs',
            metavar='HID,...'
        )
        self.parser.add_argument(
            '-a', '--attribute',
            action='store',
            dest='attributes',
            type=str,
            help='Limit polling to given Attribute IDs',
            metavar='AID,...'
        )

def main():
    pollc = RnmsPollCmd('att_disc')
    return pollc.run()

if __name__ == '__main__':
    sys.exit(main())
