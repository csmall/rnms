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
from sqlalchemy import and_

from rnms.lib.resources import chart_min_js
from rnms.lib import states
from rnms.model import DBSession, Attribute

__all__ = ['DoughnutGraph', 'AttributeStateDoughnut']

default_colors = (
        '#34495E',
        '#9B59B6',
        '#9CC2CB',
        '#1ABB9C',
        '#3498DB',
        )


class DoughnutGraph(twc.Widget):
    """
    Doughnut sized graph
     """
    template = 'rnms.templates.widgets.doughnut_graph'
    graph_title = twc.Param('Title above the graph', default='')
    label_title = twc.Param('Title above the labels', default='')
    value_title = twc.Param('Title above the labels', default='')
    graph_data = twc.Param('List of (label,value)')
    graph_colors = twc.Param('List of graph colors in hex string',
                             default=None)

    def prepare(self):
        self.resources.append(chart_min_js)
        if self.graph_colors is None:
            self.graph_colors = default_colors
        super(DoughnutGraph, self).prepare()


class AttributeStateDoughnut(DoughnutGraph):
    """
    Doughnut graph showing attributes
    """
    graph_colors = ["#468847", "#F89406", "#B94A48", "#999999",
                    "#3887AD", "#222222"]
    label_title = 'State'
    value_title = 'Attributes'
    host_id = twc.Param('Optional host ID to filter attributes', default=None)

    def prepare(self):
        conditions = []
        self.graph_data = []
        mystates = (['Up', states.STATE_UP], ['Alert', states.STATE_ALERT],
                    ('Down', states.STATE_DOWN),
                    ('Admin Down', states.STATE_ADMIN_DOWN),
                    ('Testing', states.STATE_TESTING),
                    ('Unknown', states.STATE_UNKNOWN),
                    )
        if self.host_id is not None:
            conditions.append(Attribute.host_id == self.host_id)
        for label, match in mystates:
            self.graph_data.append(
                    (label,
                     DBSession.query(Attribute).
                     filter(and_(*
                            conditions +
                            [Attribute.state_id == match])).count()))
        super(AttributeStateDoughnut, self).prepare()
