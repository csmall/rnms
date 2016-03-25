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
import json

from rnms.lib.resources import c3_min_js, c3_min_css, d3_min_js
from rnms.lib.chart_filler import ChartFiller

__all__ = ['C3Chart', ]


class C3Chart(twc.Widget):
    """
    Charts based on the C3.js set
     """
    template = 'rnms.templates.widgets.c3chart'
    show_legend = twc.Param('Boolean: show the legend or not', default=False)
    attribute = twc.Param('Attribute to graph')
    graph_type = twc.Param('Graph type to graph')
    chart_height = twc.Param('Fixed height of chart', default=None)

    def __init__(self, *args, **kw):
        self.data_groups = None
        self.data_colors = None
        self.data_names = None
        self.data_types = None
        self.data_options = None
        super(C3Chart, self).__init__(*args, **kw)

    def prepare(self):
        self.resources.append(c3_min_js)
        self.resources.append(d3_min_js)
        self.resources.append(c3_min_css)
        self._fill_data_names()
        self._fill_data_colors()
        self._fill_data_types()
        self._fill_data()
        super(C3Chart, self).prepare()

    def _fill_data_names(self):
        """ All the chart options in the data section go here """
        labels = {}
        if self.graph_type.template == 'mtuarea':
            labels['data1'] = self.graph_type.lines[0].\
                formatted_legend(self.attribute)
            labels['data2'] = self.graph_type.lines[2].\
                formatted_legend(self.attribute)
        else:
            for idx, line in enumerate(self.graph_type.lines):
                labels['data{}'.format(idx+1)] =\
                    line.formatted_legend(self.attribute)

        if labels != {}:
            self.data_names = json.dumps(labels)

    def _fill_data(self):
        cf = ChartFiller(self.attribute, self.graph_type)
        cf.calc_data()
        self.data_columns = json.dumps(cf.datasets)
        self.mins = json.dumps(cf.mins)
        self.maxs = json.dumps(cf.maxs)
        self.lasts = json.dumps(cf.lasts)

    def _fill_data_colors(self):
        """ Return JSON string of chart data colors """
        if self.graph_type.template == 'inout':
            self.data_colors = '{data1: \'#96Ca59\', data2: \'#0000ff\'}'
        elif self.graph_type.template == 'area':
            self.data_colors = '{data1: \'#96Ca59\'}'
        elif self.graph_type.template == 'mtuarea':
            self.data_colors = '{data1: \'#96Ca59\', data2: \'#ffa500\'}'

    def _fill_data_types(self):
        """ Return JSON string of chart data types """
        if self.graph_type.template == 'inout':
            self.data_types = '{data1: \'area-spline\', data2: \'spline\'}'
        elif self.graph_type.template == 'area':
            self.data_types = '{data1: \'area-spline\'}'
        elif self.graph_type.template == 'mtuarea':
            self.data_types = '{data1: \'area-step\', data2: \'area-step\'}'
            self.data_groups = '[[\'data1\', \'data2\']]'
