
# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012,2013 Craig Small <csmall@enc.com.au>
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
"""
 This file holds the table structures, which are inherited by TableBase or
 FillerBase objects, that are used in the admin system.  For objects outside
 the admin system, put them into the structures file.
"""
from rnms import model
from structures import base_table

class attribute(base_table):
    __entity__ = model.Attribute
    __limit_fields__ = ('id', 'host', 'attribute_type', 'display_name',) 

class host(base_table):
    __entity__ = model.Attribute
    __limit_fields__ = ('id', 'zone', 'display_name', 'mgmt_address',
                        'snmp_comminity', )

class zone(base_table):
    __entity__ = model.Zone
    __limit_fields__ = ('id', 'display_name', 'short_name',)
