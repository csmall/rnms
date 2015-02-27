# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2015 Craig Small <csmall@enc.com.au>
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
""" Events Widgets """

from rnms.lib import structures
from rnms.lib.table import jqGridTableBase


class EventGrid(structures.event, jqGridTableBase):
    __url__ = '/events/griddata'
    __grid_id__ = 'events-grid'
    __caption__ = 'Events'
    toolbar_items = '''\
<div class=\\"btn-group btn-group-xs\\">\
<button id=\\"tb-search\\" type=\\"button\\" class=\\"btn btn-default\\">\
<span class=\\"glyphicon glyphicon-search\\">\
</span> Search</button>\
<button id=\\"refresh-button\\" type=\\"button\\" class=\\"btn btn-success\\">\
<span class=\\"glyphicon glyphicon-refresh\\">\
</span> Reload</button>\
</div>\
'''
