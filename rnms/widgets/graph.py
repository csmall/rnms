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
""" RRD Graphs

There are several templates which broadly describe the type of graph that
will be produced

inout
-----
Used for input/output graphs. Has the standard area/line with the
input being a green area and the output being a blue line


"""
import logging
import time
from base64 import b64encode

import rrdtool
import operator

from tg import tmpl_context, flash, url

from tw2 import forms as twf
import tw2.core as twc
from tw2.jqplugins.jqplot import JQPlotWidget
from tw2.jqplugins.jqplot.base import dateAxisRenderer_js, barRenderer_js,\
        enhancedLegendRenderer_js
from sqlalchemy import distinct

from rnms.model import DBSession, GraphType, Attribute
from rnms.lib.parsers import fill_fields

logger = logging.getLogger('rnms')

SI_UNITS = (('T', 1e12),('G',1e9), ('M',1e6),('k',1e3),('',1),('m',0.001))

class GraphDatePicker(twf.CalendarDatePicker):
    date_format = '%Y/%m/%d %H:%M'
    picker_shows_time = True

    @classmethod
    def time2epoch(self, time_string):
        if time_string is None or time_string == '':
            return int(time.time())
        return int(time.mktime(time.strptime(time_string, self.date_format)))


class GraphDatePresetWidget(twf.SingleSelectField):
    """
    Selection Widget for pre-set times used for graphing
    """
    picker_shows_time=True
    date_format = '%Y/%m/%d %H:%M'
    value = 3600

    def __init__(self,**kw):
        hour = 3600
        day = 24*3600
        self.options = (
                (0,          u'No Preset'),
                (600,        u'10 Minutes'),
                (1800,       u'Half Hour'),
                (hour,       u'Hour'),
                (hour*6,     u'6 Hours'),
                (day,        u'Day'),
                (day*2,      u'2 Days'),
                (day*7,      u'Week'),
                (day*30,     u'Month'),
                (day*365,    u'Year'),
                )
        super(GraphDatePresetWidget, self).__init__()

    def prepare(self):
        try:
            self.value = int(tmpl_context.form_values['preset_time'])
        except (KeyError,TypeError):
            pass
        super(GraphDatePresetWidget, self).prepare()

class GraphTypeSelector(twf.MultipleSelectField):
    """
    Select the graph type based upon the attribute type
    """
    name='gt'
    #id='graph-type'
    graph_type_id=None

    def prepare(self):
        self.options = ()

        try:
            att_ids = [ int(x) for x in
                       tmpl_context.form_values['a'].split(',')]
        except (KeyError, ValueError):
            pass
        else:
            graph_types = DBSession.query(
                distinct(GraphType.id), GraphType.display_name).\
                    filter(GraphType.attribute_type_id.in_(
                           DBSession.query(
                               distinct(Attribute.attribute_type_id)).filter(
                                   Attribute.id.in_(att_ids))
                          ))
            self.options = tuple(gt for gt in graph_types)
            try:
                self.value = tmpl_context.form_values['gt']
            except KeyError:
                pass
        super(GraphTypeSelector, self).prepare()

class GraphWidget2(twc.Widget):
    template = 'rnms.templates.widgets.graph'

    def prepare(self):
        end_time = int(time.time())
        start_time = end_time - 3600*24
        self.url = '/graphs/image/1/27/{}/{}'.format(
            start_time, end_time)


class GraphWidget(twc.Widget):
    id='graph-widget'
    template = 'rnms.templates.graphwidget'
    title = ''
    legend = []
    img_width = ''
    img_height = ''
    img_data = ''
    start_time = None
    end_time = None

    attribute = twc.Param('Attribute to graph on')
    graph_type = twc.Param('Graph Type to use')

    def create_legend(self, graphv):
        """
        Extract the print[n] line out of graphv and make it into a legend
        """
        self.legend = []
        print_strings = {}
        for k,v in graphv.items():
            if k[:5] == 'print':
                bracket = k.find(']')
                if bracket > 6:
                    print_strings[k[6:bracket]] = v
        current_row=[]
        add_space = False
        for pkey in sorted(print_strings.iterkeys()):
            if add_space:
                current_row.append('  ')
            if len(print_strings[pkey]) > 2 and print_strings[pkey][-2] == '\\':
                current_row.append(print_strings[pkey][:-2])
                if print_strings[pkey][-1] == 'g':
                    add_space = False
                else:
                    self.legend.append((print_strings[pkey][-1], fill_fields(''.join(current_row),attribute=self.attribute)))
                    current_row=[]
                    add_space = False
            else:
                current_row.append(print_strings[pkey])
                add_space = True
        if current_row != []:
            self.legend.append(('l', fill_fields(''.join(current_row), attribute=self.attribute)))


    def get_graphv(self):
        """ Set the values for this widget using the output of graphv
        """
        if not hasattr(self, 'graph_type'):
            raise ValueError, 'graph_type must be defined'
        graph_type = getattr(self, 'graph_type')

        if not hasattr(self, 'attribute'):
            raise ValueError, 'attribute must be defined'
        attribute = getattr(self, 'attribute')

        graph_definition = graph_type.format(attribute)
        graph_options = graph_type.graph_options(attribute, self.start_time, self.end_time)
        #print graph_options + graph_definition
        try:
            graphv = rrdtool.graphv('-', graph_options + graph_definition)
        except TypeError as errmsg:
            flash('RRDTool error: {}'.format(errmsg),'error')
        except rrdtool.error as errmsg:
            flash('RRDTool error: {}'.format(errmsg), 'error')
        else:
            self.create_legend(graphv)
            self.img_data = b64encode(graphv['image'])
            self.img_width = graphv['image_width']
            self.img_height = graphv['image_height']

    def prepare(self):
        self.get_graphv()
        self.tg_url = url
        super(GraphWidget, self).prepare

class GraphWidget2(JQPlotWidget):
    id='graph-widget'
    attribute_id = None
    graph_type_id = None
    preset_time = None

    def __init__(self):
        self.end_time = time.time()
        self.start_time = self.end_time - 3600
        super(GraphWidget2, self).__init__()


    def prepare(self):
        if self.attribute_id is None:
            return None
        self.attribute = Attribute.by_id(self.attribute_id)
        if self.attribute is None:
            return None
        self.graph_type = GraphType.by_id(self.graph_type_id)
        if self.graph_type is None:
            return None
        if self.preset_time is not None:
            self.end_time = 'now'
            self.start_time = '-{}min'.format(self.preset_time)
        self.prepare_graph_template()
        self.data = self.get_data()
        self.options['title'] = self.get_title()
        self.resources.append(dateAxisRenderer_js)
        self.resources.append(barRenderer_js)
        self.resources.append(enhancedLegendRenderer_js)
        super(GraphWidget2, self).prepare()

    def get_title(self):
        """ Create the Graph Title """
        return '{} {} - {}'.format(
            self.attribute.host.display_name,
            self.attribute.display_name,
            self.graph_type.display_name,
        )
    def format_value(self, fmt, value):
        if value is None:
            return 0.0
        mult_pos = fmt.find('%s')
        if mult_pos > -1:
            si_unit, divisor = self.get_si_unit(value)
            fmt = fmt.replace('%s',si_unit)
            value = value/float(divisor)
        else:
            mult_pos = fmt.find('%S')
            if mult_pos > -1:
                si_unit, divisor = self.get_si_unit(value)
                fmt = fmt.replace('%S',si_unit)
                value = value/float(divisor)
        return fmt % value

    def get_si_unit(self, value):
        """ Return unit,divisor tuple for SI unit eg 2000 = k,1000 """
        for unit,divisor in SI_UNITS:
            if value >= divisor:
                return unit,divisor
        return unit,divisor

    def get_data(self):
        data = []
        multiplier_row = []
        for line_idx,rrd_line in enumerate(self.graph_type.rrd_lines):
            rrd = rrd_line.attribute_type_rrd
            if rrd_line.multiplier == '':
                multiplier_op = None
            else:
                multiplier_val,mop_name = fill_fields(rrd_line.multiplier,
                                                      attribute=self.attribute).split(',')
                multiplier_val = float(multiplier_val)
                # FIXME = make this more generic
                if mop_name == '*':
                    multiplier_op = operator.mul
                elif mop_name == '/':
                    multiplier_op = operator.div
                else:
                    raise ValueError

            rrd_values = rrd.fetch(self.attribute_id, self.start_time,
                                   self.end_time)
            if self.graph_type.template == 'multotarea':
                # The first series is the multiplier
                if multiplier_row == []:
                    multiplier_row = rrd_values[2]
                    continue
            start_time, end_time, step = rrd_values[0]
            val_time = start_time
            rowval = []
            row_max = None
            row_sum = 0.0
            row_len = 0.0
            for idx,val in enumerate(rrd_values[2]):
                if val[0] is not None:
                    if multiplier_op is None:
                        value = val[0]
                    else:
                        value = multiplier_op(val[0],multiplier_val)
                    if self.graph_type.template == 'multotarea':
                        mul = multiplier_row[idx][0]
                        if mul is not None:
                            value *=  mul
                        print value
                    if row_max is None or row_max < value:
                        row_max = value
                    row_sum += value
                    row_len += 1
                    rowval.append((val_time*1000,value))
                val_time += step
            if row_len > 0:    
                data.append(rowval)
                self.set_series_label(line_idx, rrd_line,
                                      row_max, row_sum, row_len,
                                      rowval[-1][1])
        return data

    def set_series_label(self, idx, rrd_line, row_max, row_sum, row_len, row_last):
        label = {
            'label': '{} - Max: {} Average: {} Last: {}'.format(
                rrd_line.legend,
                self.format_value(
                    rrd_line.legend_unit,
                    row_max),
                self.format_value(
                    rrd_line.legend_unit,
                    row_sum/float(row_len)),
                self.format_value(
                    rrd_line.legend_unit,
                    row_last)
            )
        }
        try:
            self.options['series'][idx].update(label)
        except IndexError:
            self.options['series'].append(label)

    def prepare_graph_template(self):
        """ Setup the graph template specific options """
        # First the common options
        self.options = {
            'seriesDefaults':{
#                'renderer': twc.js_symbol('$.jqplot.BarRenderer'),
                'rendererOptions': { 'fillToZero': True},
                'showMarker': False,
            },
            'series': [],
            'legend':{
                'show': True,
                'location': 's',
                'placement': 'outsideGrid',
            },
            'axes':{
                'xaxis': {
                    'renderer': twc.js_symbol('$.jqplot.DateAxisRenderer'),
                    'tickOptions': { 'formatString': '%H:%M'},
                    'pad': 0,
                },
                'yaxis': {
                    'min': 0,
                    'forceTickAt0': True,
                    'tickOptions': {'formatter': twc.js_symbol('tickFormatter')},
                    'autoscale': True,
                }
            }
        }
        if self.graph_type.template == 'inout':
            #self.options['seriesDefaults']['renderer']=twc.js_symbol('$.jqplot.BarRenderer')
            self.options['seriesColors'] = ( '#00cc00', '#0000ff')
            self.options['series'] = [
                {'fill':True,
                 'fillAndStroke': True,
                 'fillColor': '#ade7ad'},
                {'fill':False,},
            ]

        if self.graph_type.template == 'totalarea':
            self.options['stackSeries'] = True
            self.options['seriesColors'] = ( '#ff8800', '#00cc00')
            self.options['seriesDefaults'].update({'fill':True,'fillAndStroke':False})
        elif self.graph_type.template == 'stackedarea':
            self.options['stackSeries'] = True
            self.options['seriesDefaults'].update({'fill':True,'fillAndStroke':True})
            self.options['axes']['yaxis'].update({'max':100})
        elif self.graph_type.template == 'multotarea':
            self.options['seriesColors'] = ( '#ade7ad', '#ff8800' )
            self.options['seriesDefaults'].update({'fill':True})
