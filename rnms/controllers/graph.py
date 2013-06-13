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
"""RRD Graph controller module"""

import logging
import time
import datetime
import rrdtool

# turbogears imports
from tg import validate, flash, expose, tmpl_context
from formencode import validators
from tw2 import forms as twf
from tw2 import core as twc
from sqlalchemy import and_

# project specific imports
from rnms.lib.base import BaseController
from rnms.model import DBSession, GraphType, Attribute
from rnms.widgets.graph import GraphDatePresetWidget, GraphDatePicker, GraphTypeSelector, GraphWidget
from rnms.widgets import InfoBox

logger = logging.getLogger('rnms')

class GraphForm2(twf.Form):
    class child(twf.TableLayout):
        graph_types = GraphTypeSelector()
        preset_time = GraphDatePresetWidget()
        start_time = GraphDatePicker()
        end_time = GraphDatePicker()

class GraphController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = predicates.not_anonymous()

    @expose('rnms.templates.widget')
    def blah(self):
        from rnms.widgets.graph import GraphWidget2
        w = GraphWidget2
        return dict(w=w)
    
    @expose(content_type='images/png')
    @validate(validators={'a':validators.Int(min=1),
                          'gt':validators.Int(min=1),
                          'st':validators.Int(min=1),
                          'et':validators.Int(min=1)
                         })
    def image(self, a, gt, st, et):
        """ Returns a RRDgraph """
        if tmpl_context.form_errors:
            return tmpl_context.form_errors
        attribute = Attribute.by_id(a)
        if attribute is None:
            logger.error('Attribute %d does not exist', a)
            return
        graph_type = GraphType.by_id(gt)
        if graph_type is None:
            logger.error('GraphType %d does not exist', gt)
            return
        if graph_type.attribute_type_id != attribute.attribute_type_id:
            logger.error('GraphType %d is not for Attribute %d',gt,a)
            return
        graph_definition = graph_type.format(attribute)
        graph_options = graph_type.graph_options(attribute, st,et)
        try:
            graphv = rrdtool.graphv('-', graph_options + graph_definition)
        except TypeError as errmsg:
            logger.error('RRDTool error: {}'.format(errmsg))
        except rrdtool.error as errmsg:
            logger.error('RRDTool error: {}'.format(errmsg))
        else:
            return graphv['image']


    @expose('rnms.templates.graph')
    @validate(validators={'a':validators.String(), 'gt':validators.Set(), 'preset_time':validators.Int(), 'start_time':validators.String(), 'end_time':validators.String()})
    def index(self, a=[], gt=[], preset_time=0, start_time=0, end_time=None, **kw):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        try:
            att_ids = [int(x) for x in a.split(',')]
        except ValueError:
            flash('Bad Attribute IDs', 'error')
            return {}
        try:
            gt_ids = [int(x) for x in gt]
        except ValueError:
            flash('Bad GraphType IDs', 'error')
            return {}

        graph_widgets=[]
        if att_ids != [] and gt_ids != []:
            if preset_time is not None and preset_time > 0:
                end_timestamp = int(time.time())
                start_timestamp = end_timestamp - preset_time
            else:
                end_timestamp = GraphDatePicker.time2epoch(end_time)
                start_timestamp = GraphDatePicker.time2epoch(start_time)

            graphs = DBSession.query(Attribute,GraphType).\
                    filter(and_(
                        Attribute.attribute_type_id ==
                        GraphType.attribute_type_id,
                        Attribute.id.in_(att_ids),
                        GraphType.id.in_(gt_ids)
                    )).order_by(GraphType.id,Attribute.host_id)
            for attribute, graph_type in graphs:
                gw = GraphWidget()
                gw.attribute = attribute
                gw.graph_type = graph_type
                gw.start_time = start_timestamp
                gw.end_time = end_timestamp
                gwbox = InfoBox()
                gwbox.title = graph_type.title(attribute)
                gwbox.child_widget = gw
                graph_widgets.append(gwbox)

        selectionbox = InfoBox()
        selectionbox.title = 'Graph Selection'
        selectionbox.child_widget = GraphForm2()
        return dict(page='graph',
                    selectionbox=selectionbox, graph_widgets=graph_widgets)

    #@expose(content_type='image/png')
    @expose('rnms.templates.graph_image')
    @validate(validators={'a':validators.Int(), 'gt':validators.Int(), 'start_time':validators.Int(),'end_time':validators.Int()})
    def graph(self, a, gt, start_time=0, end_time=0, **kw):
        attribute = Attribute.by_id(a)
        if attribute is None:
            logger.error('Attribute %d does not exist', a)
            return
        graph_type = GraphType.by_id(gt)
        if graph_type is None:
            logger.error('GraphType %d does not exist', gt)
            return
        if graph_type.attribute_type_id != attribute.attribute_type_id:
            logger.error('GraphType %d is not for Attribute %d',gt,a)
            return

        gw = GraphWidget()
        gw.attribute = attribute
        gw.graph_type = graph_type
        return dict(gw=gw)


    @expose('rnms.templates.widget')
    def test(self, a):
        from tw2.jqplugins import jqplot
        from tw2.jqplugins.jqplot.base import dateAxisRenderer_js#, barRenderer_js
        attribute = Attribute.by_id(a)
        rrd = attribute.attribute_type.rrds[0]
        rrd_values = rrd.fetch(attribute, '-60min','now')
        # populate the data
        graph_data = []
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(minutes=60)
        step_time = datetime.timedelta(seconds=((end_time - start_time).total_seconds() / len(rrd_values[2])))
        value_time = start_time
        graph_data = []
        last_value = None
        for value in rrd_values[2]:
            if value[0]:
                if last_value is not None:
                    graph_data.append((value_time.ctime(), float(value[0])*8.0))
                last_value = value[0]
            else:
                graph_data.append((value_time.ctime(), None))
            value_time += step_time

        class DemoWidget(jqplot.JQPlotWidget):
            id='foo-bat'
#            data = [[[1, 2],[3,5.12],[5,13.1],[7,33.6],[9,85.9],[11,219.9]]]
            data3 = [[('13121324651', '20'), ('13121325651', '25')]]
            data = [[
                ('2012-12-12 20:20', 200),
                ('2012-12-12 20:25', 100),
                ]]
            a = [[
                ('2012-12-12 20:30', 6.8531193021e+05),
                ('2012-12-12 20:35', 9.5605499862e+05),
                ('2012-12-12 20:40', 1.0866987097e+05),
                    ]]

            options = {
                    'title': 'foo',
                    'grid': {'background': 'rgb(255,255,255)', },
                    'seriesDefaults': {
                        'markerOptions': { 'show': False,},
                        'fill': True,
                        'fillAndStroke': True,
                        #'fillColor': 'rgb(255,128,128)',
                        'fillAlpha': '0.5',
                        },
                    'axes' :{
                        'xaxis': {
                            'renderer' : twc.js_symbol('$.jqplot.DateAxisRenderer'),
                            'tickOptions': { 'formatString': '%H:%M' },
                            'pad': 0,
                        },
                        'yaxis': {
                            'min': 0,
                            'pad': 0,
                            },
                        },
                    }

            def prepare(self):
                self.resources.append(dateAxisRenderer_js)
                super(DemoWidget, self).prepare()

        w = DemoWidget()
        w.data = (graph_data,)
        w.options['axes']['xaxis']['max'] = end_time.ctime()
        return dict(widget=w)

