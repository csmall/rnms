# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011-2014 Craig Small <csmall@enc.com.au>
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
#
""" Host related database entries """
config_transfers = (
    (u'No Configuration Transfer', u''),
    (u'Cisco IOS, > 12.0 (CONFIG-COPY-MIB)', u'cisco_cc'),
    (u'Cisco IOS, < 12.0 (SYS-MIB)', u'cisco_sys'),
    (u'Cisco CatOS (STACK-MIB)', u'cisco_catos'),
    (u'Alteon WebOS Switches (DANGEROUS)', u'alteon_webos'),
)

autodiscovery_policies = (
    (u'No Autodiscovery',
        True, False, False, False, False, False,  True,  True,  True),
    (u'Standard',
        True,  True, False,  True, False,  True,  True,  True,  True),
    (u'Automagic',
        True,  True,  True,  True,  True, False,  True,  True,  True),
    (u'Administrative',
        False,  True,  True,  True, False,  True,  True,  True,  True),
    (u'Just Inform',
        False, False, False,  True, False, False, False,  True,  True),
    (u'Standard (for Switches)',
        True,  True, False,   True,  True, False,  True,  True, False)
)
