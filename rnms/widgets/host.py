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
from tw2.jqplugins.jqgrid import jqGridWidget
from tw2.jqplugins.jqgrid.base import word_wrap_css
from tw2.jqplugins.jqplot import JQPlotWidget
from tw2.jqplugins.jqplot.base import categoryAxisRenderer_js, barRenderer_js
from tw2 import core as twc

from math import sin, cos

from time import time


class HostsGrid(jqGridWidget):
    id = 'hosts-grid-id'
    options = {
            'pager': 'hosts-grid-pager',
            'url': '/hosts/griddata',
            'colNames': [ 'Host Name', 'Zone' ],
            'datatype': 'json',
            'colModel' : [
                {
                    'name': 'display_name',
                    'width': 30,
                    'align': 'left',
                },{
                    'name': 'zone_display_name',
                    'width': 30,
                    'align': 'left',
                }],
            'viewrecords': True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'width': 900,
            'height': 'auto',
            }
    def prepare(self):
        self.resources.append(word_wrap_css)
        super(HostsGrid, self).prepare()

#########################
def make_data():
    """ Sin of the times! """
    now = int(time())
    n = 20.0
    tsteps = 100
    tspan = range(now - tsteps, now)
    series1 = [[i * 1000, sin(i / n)] for i in tspan]
    series2 = [[i * 1000, abs(sin(i / n)) ** ((i % (2 * n)) / n)]
               for i in tspan]
    series3 = [[i * 1000, cos(i / (n + 1)) * 1.5] for i in tspan]
    series4 = [[series2[i][0], series2[i][1] * series3[i][1]]
               for i in range(len(series3))]
    data = [series1, series2, series3, series4]
    return data

data = make_data()

class LogPlot(JQPlotWidget):
    id = 'pie-test'
    resources = JQPlotWidget.resources + [
            categoryAxisRenderer_js,
            barRenderer_js
            ]
    data = data

    options = {
            'seriesDefaults' : {
                'renderer': twc.js_symbol('$.jqplot.BarRenderer'),
                'rendererOptions': { 'barPadding': 4, 'barMargin': 10 }
                },
            'axes' : {
                'xaxis': {
                    'renderer': twc.js_symbol(src="$.jqplot.CategoryAxisRenderer"),
                    },
                'yaxis': {'min': 0, },
                }
            }


