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
#
""" Hosts Widgets """
from rnms.lib import structures
from rnms.lib.table import jqGridTableBase

class ZoneGrid(structures.zone, jqGridTableBase):
    __grid_id__ = 'zone-grid'
    __url__ = '/zones/griddata'
    __omit_fields__ = ('__actions__',)
    __caption__ = 'Zones'

