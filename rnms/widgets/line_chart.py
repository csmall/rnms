# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2016 Craig Small <csmall@enc.com.au>
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
import tw2.core as twc
from tg import url

from rnms.lib.resources import chart_min_js

__all__ = ['LineChart', ]


class LineChart(twc.Widget):
    """
    Line Charts
     """
    template = 'rnms.templates.widgets.line_chart'
    data_url = twc.Param('URL for fetching the JSON data for graph')

    def prepare(self):
        self.resources.append(chart_min_js)


class AttributeLineChart(LineChart):
    attribute_id = twc.Param('Attribute ID for the graph')
    graph_type_id = twc.Param('Graph Type ID', default=None)

    def prepare(self):
        if self.graph_type_id is None:
            self.graph_type_id = 34  # FIXME
        self.data_url = url(
            '/graphs/linedata.json',
            {'a': self.attribute_id,
             'gt': self.graph_type_id})
        super(AttributeLineChart, self).prepare()
