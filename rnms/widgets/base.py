# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2013-2016 Craig Small <csmall@enc.com.au>
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
from tg import url

import tw2.core as twc


class MapWidget(twc.Widget):
    template = 'rnms.templates.widgets.map'

    def __init__(self, **kw):
        self.url = url
        self.map_groups = {}
        super(MapWidget, self).__init__(**kw)

    def add_item(self, group_id, group_name, group_data, new_item):
        """ Add the given item to the relevant map_group """
        try:
            self.map_groups[group_id]['items'].append(new_item)
        except KeyError:
            self.map_groups[group_id] = {
                'group': group_name,
                'group_fields': group_data,
                'items': [new_item]}


class Row(twc.CompoundWidget):
    """
    Bootstrap row element
    """
    template = 'rnms.templates.widgets.row'


class Text(twc.Widget):
    """
    Very simple widget that just displays text.
    The template should be defined which is the text to put put into the Widget
    """
    pass
