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
import json

from rnms.lib.resources import c3_min_js, c3_min_css, d3_min_js

__all__ = ['C3Chart', ]


class C3Chart(twc.Widget):
    """
    Charts based on the C3.js set
     """
    template = 'rnms.templates.widgets.c3chart'
    show_legend = twc.Param('Boolean: show the legend or not', default=False)
    attribute = twc.Param('Attribute to graph')
    graph_type = twc.Param('Graph type to graph')

    def prepare(self):
        self.resources.append(c3_min_js)
        self.resources.append(d3_min_js)
        self.resources.append(c3_min_css)
        self.data_url = url(
            '/graphs/attribute.json',
            {'a': self.attribute.id, 'gt': self.graph_type.id})
        self.data_names = self._get_data_names()
        self.data_colors = self._get_data_colors()
        self.data_types = self._get_data_types()
        super(C3Chart, self).prepare()

    def _get_data_names(self):
        """ Return javascript version of the name: label dict """
        labels = {}
        for idx, line in enumerate(self.graph_type.lines):
            labels['data{}'.format(idx+1)] =\
                line.formatted_legend(self.attribute)
        return json.dumps(labels)

    def _get_data_colors(self):
        """ Return JSON string of chart data colors """
        if self.graph_type.template == 'inout':
            return '{data1: \'#96Ca59\', data2: \'#0000ff\'}'
        elif self.graph_type.template == 'area':
            return '{data1: \'#96Ca59\'}'
        return None

    def _get_data_types(self):
        """ Return JSON string of chart data types """
        if self.graph_type.template == 'inout':
            return '{data1: \'area-spline\', data2: \'spline\'}'
        elif self.graph_type.template == 'area':
            return '{data1: \'area-spline\'}'
        return None
