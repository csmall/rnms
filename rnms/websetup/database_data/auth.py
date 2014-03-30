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
""" Authentication entries """

# Name, description
permissions = (
    (u'manage', u'Access to Admin screens'),
    (u'UserRO', u'Read-Only Access to User, Group and Permissions'),
    (u'UserRW', u'Read/Write Access to User, Group and Permissions'),
    (u'HostRO', u'Read-Only Access to Host and Attribute'),
    (u'HostRW', u'Read/Write Access to Host and Attribute'),
    (u'AdminRO', u'Read-Only Access to remaining models'),
    (u'AdminRW', u'Read/Write Access to remaining models'),
)
groups = (
    (u'User View', u'Users that can view Users',
     (u'manage', u'UserRO',)),
    (u'User Admin', u'Users that can edit Edits',
     (u'manage', u'UserRW',)),
    (u'Host View', u'Users that can view hosts',
     (u'manage', u'HostRO',)),
    (u'Host Admin', u'Users that can edit Hosts',
     (u'manage', u'HostRW',)),
    (u'System View', u'Users that can view other items',
        (u'manage', u'UserRO', u'HostRO', u'AdminRO')),
    (u'System Admin', u'Users that can edit other items',
        (u'manage', u'UserRW', u'HostRW', u'AdminRW')),
)
