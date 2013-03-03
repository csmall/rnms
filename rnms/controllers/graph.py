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
import rrdtool
import time
import datetime
from base64 import b64encode

# turbogears imports
from tg import expose, config, url, tmpl_context

from tg import redirect, validate, flash
#from tg.i18n import ugettext as _
#from tg import predicates
from formencode import validators
from tw2.jqplugins import portlets
from tw2 import forms as twf
from tw2 import core as twc
from tw2.jqplugins.ui import set_ui_theme_name

# project specific imports
from rnms.lib.base import BaseController
from rnms import model
#from rnms.model import DBSession, metadata
from rnms.widgets.graph import GraphDatePresetWidget, GraphDatePicker, GraphTypeSelector, GraphWidget

logger = logging.getLogger('rnms')

class GraphForm2(twf.Form):
    class child(twf.TableLayout):
        graph_types = GraphTypeSelector()
        preset_time = GraphDatePresetWidget()
        start_time = GraphDatePicker()
        end_time = GraphDatePicker()

    def __init__(self, *args, **kwargs):
        print self.child.children[0]
        super(GraphForm2, self).__init__()

class GraphLayout(portlets.ColumnLayout):
    id='graph-layout'
    graph_type_id=0

    def display(self,gt):
        portlets.ColumnLayout.display(self)

    class porlet1(portlets.Portlet):
        title = 'Events'
        class GraphForm(twf.TableForm):
            pass#graph_type = GraphType()
def yaxis_format(value='foo'):
    print 'value', value
    return 'fff {}'.format(value)

class GraphController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = predicates.not_anonymous()
    

    @expose('rnms.templates.graph')
    @validate(validators={'a':validators.Int(), 'gt':validators.Set(), 'preset_time':validators.Int(), 'start_time':validators.String(), 'end_time':validators.String()})
    def _default(self, a, gt=[], preset_time=0, start_time=0, end_time=None, **kw):
        try:
            preset_time = int(kw['graph-layout:col1:graph-form:preset_time'])
        except KeyError:
            preset_time = 0

        graph_portlets=[]
        if gt is not None and gt != '':
            if preset_time is not None and preset_time > 0:
                end_timestamp = int(time.time())
                start_timestamp = end_timestamp - preset_time
            else:
                end_timestamp = GraphDatePicker.time2epoch(end_time)
                start_timestamp = GraphDatePicker.time2epoch(start_time)

            attribute = model.Attribute.by_id(a)
            if attribute is None:
                flash('Attribute not found')
            for gt_row in gt:
                try:
                    gt_id = int(gt_row)
                except ValueError:
                    pass
                else:
                    graph_type = model.GraphType.by_id(gt_id)
                    if graph_type is not None:
                        title = ''#attribute.host.display_name + ' ' + attribute.display_name + ' ' + graph_type.display_name
                        portlet_id = 'graph-' + str(graph_type.id)
                        gw_portlet = portlets.Portlet(id=portlet_id, title=title)
                        gw = GraphWidget()
                        gw.attribute = attribute
                        gw.graph_type = graph_type
                        gw.start_time = start_timestamp
                        gw.end_time = end_timestamp
                        gw_portlet.children = (gw,)
                        graph_portlets.append(gw_portlet)

        por = portlets.Portlet(id='graph-form', title='Graph Selection')
        por.children = [GraphForm2(),]
        
        class LayoutWidget(portlets.ColumnLayout):
            id = 'graph-layout'
            class col1(portlets.Column):
                width = '100%'
                children = [por] + graph_portlets
                #class por1(portlets.Portlet):
                #    title = 'Graph Selection'
                #    form = GraphForm2()
                #class por2(portlets.Portlet):
                #    title='Graphs'
                #    children = graph_widgets

        return dict(form=LayoutWidget, graph_widgets=[])

    #@expose(content_type='image/png')
    @expose('rnms.templates.graph_image')
    @validate(validators={'a':validators.Int(), 'gt':validators.Int(), 'start_time':validators.Int(),'end_time':validators.Int()})
    def graph(self, a, gt, start_time=0, end_time=0, **kw):
        attribute = model.Attribute.by_id(a)
        if attribute is None:
            logger.error('Attribute %d does not exist', a)
            return
        graph_type = model.GraphType.by_id(gt)
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
        from tw2.jqplugins.jqplot.base import dateAxisRenderer_js, barRenderer_js
        attribute = model.Attribute.by_id(a)
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

    @expose()
    def test2(self, a):
        return str(rrd)
