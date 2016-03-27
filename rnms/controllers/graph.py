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
"""RRD Graph controller module"""

import logging

# turbogears imports
from tg import validate, expose, tmpl_context, predicates, flash, url
from formencode import validators
import tw2.core as twc

# project specific imports
from rnms.lib.resources import c3_min_js, c3_min_css, d3_min_js
from rnms.lib.base import BaseController
from rnms.lib.chart_filler import ChartFiller
from rnms.model import DBSession, GraphType, Attribute
from rnms.widgets import PanelTile, GraphSelector, C3Chart, TimeSelector

logger = logging.getLogger('rnms')


class GraphController(BaseController):
    allow_only = predicates.not_anonymous()

    @expose('rnms.templates.graph.index')
    @validate(validators={'a': validators.Int(min=1)})
    def index(self, a=None):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}

        class SelectPanel(PanelTile):
            title = 'Graph Selection'
            fullwidth = True

            class MyGraphSelector(GraphSelector):
                graph_url = url('/graphs/plot')
                attribute_id = a

            class MyTimeSelector(TimeSelector):
                pass

        return dict(page='graphs',
                    select_panel=SelectPanel)

    @expose('rnms.templates.graph_attribute')
    @validate(validators={'a': validators.Int(min=1)})
    def _default(self, a):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        my_attribute = Attribute.by_id(a)
        if my_attribute is None:
            flash('Attribute ID#{} not found'.format(a), 'error')
            return {}

        class SelectPanel(PanelTile):
            title = 'Select Graph'

            class MyGraphSelector(GraphSelector):
                attribute_type_id = my_attribute.attribute_type_id

        class GraphPanel(PanelTile):
            title = 'Attribute Graphs'
            fullwidth = True
            fullheight = True

            class GraphList(twc.Widget):
                template = 'rnms.templates.widgets.graphs'
                resources = [c3_min_js, d3_min_js, c3_min_css]

        return dict(attribute=my_attribute,
                    select_panel=SelectPanel,
                    graph_panel=GraphPanel)

    @expose('')
    def plot(self, a, gt, pt=None):
        """ Return the actual HTML for a graph """
        my_attribute = Attribute.by_id(a)
        my_graph_type = GraphType.by_id(gt)

        class MyPanel(PanelTile):
            title = '{} - {}'.format(
                my_attribute.host.display_name,
                my_attribute.display_name)
            subtitle = my_graph_type.formatted_title(my_attribute)
            fullwidth = True

            class MyChart(C3Chart):
                id = 'graph_{}_{}'.format(a, gt)
                attribute = my_attribute
                graph_type = my_graph_type
                chart_height = 200
                preset_time = pt

        return MyPanel().display()

    @expose('json')
    def attribute(self, a=None, gt=None):
        """
        JSON encoded data for the attribute chart
        """
        if tmpl_context.form_errors:
            return {'error': 'error'}
        chart_filler = ChartFiller(a=a, gt=gt)
        return chart_filler.display()

    @expose('rnms.templates.widgets.select')
    def types_option(self, a=None):
        if a is not None and type(a) is not list:
            a = [a]
        att_ids = [int(x) for x in a]
        atype = DBSession.query(GraphType.id, GraphType.display_name,
                                GraphType.attribute_type_id).\
            filter(GraphType.attribute_type_id.in_(
                   DBSession.query(Attribute.attribute_type_id).
                   filter(Attribute.id.in_(att_ids))
                   ))
        return dict(data_name='atype', items=atype.all())
