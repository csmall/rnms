# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012-2014 Craig Small <csmall@enc.com.au>
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
""" Status Pie
   A widget that is pie graph showing the breakdown of various status
   of the objects
   """
from tw2.jqplugins.jqplot import JQPlotWidget
from tw2.jqplugins.jqplot.base import pieRenderer_js
import tw2.core as twc

from rnms.lib import states


class StatusPie(JQPlotWidget):
    """
    Pie Chart of the Status """
    __state_list__ = (
        states.STATE_UP, states.STATE_ALERT, states.STATE_DOWN,
        states.STATE_ADMIN_DOWN, states.STATE_TESTING,
        states.STATE_UNKNOWN)
    state_data = None

    resources = JQPlotWidget.resources + [pieRenderer_js]

    options = {
        'seriesColors': ["#468847", "#F89406", "#B94A48", "#999999",
                         "#3887AD", "#222222"],
        'seriesDefaults': {
            'renderer': twc.js_symbol('$.jqplot.PieRenderer'),
            'rendererOptions': {
                'showDataLabels': True,
                'dataLabels': 'value',
                },
            },
        'legend': {
            'show': True,
            'location': 'e',
            },
        'grid': {
            'background': '#ffffff',
            'borderColor': '#ffffff',
            'shadow': False,
            },
        }

    def prepare(self):
        series = []
        if self.state_data is not None:
            for state in self.__state_list__:
                try:
                    series.append((states.STATE_NAMES[state].capitalize(),
                                   self.state_data[state]))
                except KeyError:
                    series.append((states.STATE_NAMES[state].capitalize(), 0))
        self.data = [series]
        super(StatusPie, self).prepare()
