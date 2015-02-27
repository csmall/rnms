# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2013-2015 Craig Small <csmall@enc.com.au>
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
from tw2.jqplugins.ui import jquery_ui_css
from tw2.jquery import jquery_js

class MapWidget(twc.Widget):
    template = 'rnms.templates.widgets.map'

    def __init__(self):
        self.url = url
        self.map_groups = {}
        super(MapWidget, self).__init__()

    def add_item(self, group_id, group_name, group_data, new_item):
        """ Add the given item to the relevant map_group """
        try:
            self.map_groups[group_id]['items'].append(new_item)
        except KeyError:
            self.map_groups[group_id] = {'group': group_name,
                                         'group_fields': group_data, 'items': [new_item]}
    def prepare(self):
        self.resources.append(jquery_js)
        super(MapWidget, self).prepare()

class InfoBox(twc.Widget):
    id = 'infobox'
    template = 'rnms.templates.widgets.infobox'
    text = None
    child_widget = None

    def prepare(self, text=None):
        self.resources.append(jquery_ui_css)
        super(InfoBox, self).prepare()

