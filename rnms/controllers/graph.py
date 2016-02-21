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
from tg import validate, expose, tmpl_context, predicates
from formencode import validators, ForEach

# project specific imports
from rnms.lib.base import BaseController
from rnms.lib.chart_filler import ChartFiller
from rnms.model import DBSession, GraphType, Attribute
from rnms.widgets.graph import GraphWidget
from rnms.widgets import MainMenu

logger = logging.getLogger('rnms')


class GraphController(BaseController):
    allow_only = predicates.not_anonymous()

    @expose('rnms.templates.graph_index')
    @validate(validators={'a': ForEach(validators.Int(min=1))})
    def index(self, a=None):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        if a == []:
            a = None
        return dict(page='graphs', attribute_ids=a,
                    main_menu=MainMenu())

    @expose('json')
    def attribute(self, a=None, gt=None):
        """
        JSON encoded data for the attribute chart
        """
        if tmpl_context.form_errors:
            return {'error': 'error'}
        chart_filler = ChartFiller(a=a, gt=gt)
        return chart_filler.display()

    @expose('rnms.templates.widgets.graph_widget')
    @validate(validators={'a': validators.Int(min=1),
                          'gt': validators.Int(min=1),
                          'pt': validators.Int(min=1)})
    def widget(self, a, gt, pt=None):
        if tmpl_context.form_errors:
            return dict(errmsg=' '.join(
                ['{0[1]} for {0[0]}'.format(x) for x in
                 tmpl_context.form_errors.items()]))

        class MyGraph(GraphWidget):
            id = 'graph-{}-{}'.format(a, gt)
            attribute_id = a
            graph_type_id = gt
            preset_time = pt
        #   return dict(page='graph', main_menu=MainMenu(), w=w)
        return dict(w=MyGraph)

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
