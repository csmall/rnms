# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013-2014 Craig Small <csmall@enc.com.au>
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

lines
-----
The default graph.  Each specified RRD will have its line drawn on the
same axes.

area
----
Single line that has its area filled

inout
-----
Used for input/output graphs. Has the standard area/line with the
input being a green area and the output being a blue line. Uses only
two RRDs.

ufarea
------
Stacked Area graph, for used/free.
Used is down the bottom and is orange
Free is above and in green.
RRDs: used, free

mtuarea
-------
Graph showing two areas that are stacked.
The first area is green and shows free value, the second is
orange and shows used.
RRDs: multipler, total and used in that order
Free = (total-used) * multiplier
Used = used * multiplier
The Legend and units for Free comes from the multiplier row


"""
import time

import operator

from tg import tmpl_context

from tw2 import forms as twf
import tw2.core as twc
from tw2.jqplugins.jqplot import JQPlotWidget
from tw2.jqplugins.jqplot.base import dateAxisRenderer_js, barRenderer_js,\
    enhancedLegendRenderer_js
from sqlalchemy import distinct

from rnms.model import DBSession, GraphType, Attribute
from rnms.lib.parsers import fill_fields

SI_UNITS = (
    ('T', 1e12),
    ('G', 1e9),
    ('M', 1e6),
    ('k', 1e3),
    ('', 1),
    ('m', 0.001))

# Measured in minutes
# max timespan, label, labelinterval
TICK_INTERVALS = (
    (0,         '%H:%M',    1),
    (12,        '%H:%M',    1),
    (30,        '%H:%M',    5),
    (60,        '%H:%M',    10),
    (180,       '%H:%M',    20),
    (360,       '%H:%M',    60),
    (1080,      '%H:%M',    2*60),
    (3600,      '%a %H:%M', 6*60),
    (7200,      '%a',       24*60),
    (10800,     '%d',       24*60),
    (14400,     '%a %d',    2*24*60),
    (21600,     '%a',       2*24*60),
    (64800,     'Week %V',  7*24*60),
    (129600,    'Week %V',  14*24*60),
    (1036800,   '%b',       30*24*60),
    (1892160,   '%b',       3*30*24*60),
    (5184000,   '%y',       12*30*24*60),
)


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
    picker_shows_time = True
    date_format = '%Y/%m/%d %H:%M'
    value = 3600

    def __init__(self, **kw):
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
        except (KeyError, TypeError):
            pass
        super(GraphDatePresetWidget, self).prepare()


class GraphTypeSelector(twf.MultipleSelectField):
    """
    Select the graph type based upon the attribute type
    """
    name = 'gt'
    #id='graph-type'
    graph_type_id = None

    def prepare(self):
        self.options = ()

        try:
            att_ids = [int(x) for x in
                       tmpl_context.form_values['a'].split(',')]
        except (KeyError, ValueError):
            pass
        else:
            graph_types = DBSession.query(
                distinct(GraphType.id), GraphType.display_name).\
                filter(GraphType.attribute_type_id.in_(
                    DBSession.query(
                        distinct(Attribute.attribute_type_id)).filter(
                        Attribute.id.in_(att_ids))))
            self.options = tuple(gt for gt in graph_types)
            try:
                self.value = tmpl_context.form_values['gt']
            except KeyError:
                pass
        super(GraphTypeSelector, self).prepare()


class BaseFormat(object):
    """
    Base object for all the *Format objects contained
    inside the GraphWidget. Common functions go here
    """
    parent = None

    def __init__(self, parent):
        self.parent = parent

    def get_options(self):
        """ Used to get the options of the graph"""
        raise NotImplemented

    def get_data(self):
        """ Get the data series for this graph """
        raise NotImplemented

    def get_mult(self, rrd_line):
        """ Return the muliplier operation and value, if required by
        the rrd_line, else return None,None
        """
        if rrd_line.multiplier == '':
            return None, None
        multiplier_val, mop_name = fill_fields(
            rrd_line.multiplier,
            attribute=self.parent.attribute).split(',')
        multiplier_val = float(multiplier_val)
        # FIXME = make this more generic
        if mop_name == '*':
            multiplier_op = operator.mul
        elif mop_name == '/':
            multiplier_op = operator.div
        else:
            raise ValueError
        return multiplier_op, multiplier_val

    def row_values(self, rrd_values, mult_op, mult_val):
        """ Scan the raw rrd_value list fresh from rrdfetch and
        build into sometihng jqPlot understands
        """
        rowval = []
        row_max = None
        row_sum = 0.0
        row_len = 0.0
        start_time, end_time, step = rrd_values[0]
        val_time = start_time
        for val in rrd_values[2]:
            if val[0] is not None:
                if mult_op is None:
                    value = val[0]
                else:
                    value = mult_op(val[0], mult_val)
                if row_max is None or row_max < value:
                    row_max = value
                row_sum += value
                row_len += 1
                rowval.append((val_time*1000, value))
            val_time += step
        return dict(max=row_max, sum=row_sum, len=row_len, values=rowval)

    def update_row(self, row_data, data_time, value):
        if row_data['max'] < value:
            row_data['max'] = value
        row_data['sum'] += value
        row_data['len'] += 1
        row_data['values'].append((data_time*1000, value))

    def set_series_label(self, idx, rrd_line, row_max, row_sum, row_len,
                         row_last, legend=None):
        if legend is None:
            legend = rrd_line.legend
        if row_len == 0:
            average = 'Nan'
        else:
            average = self.format_value(rrd_line.legend_unit,
                                        row_sum/float(row_len))

        label = {
            'label': '{} - Max: {} Average: {} Last: {}'.format(
                legend,
                self.format_value(
                    rrd_line.legend_unit,
                    row_max),
                average,
                self.format_value(
                    rrd_line.legend_unit,
                    row_last)
            )
        }
        try:
            self.parent.options['series'][idx].update(label)
        except IndexError:
            self.parent.options['series'].append(label)

    def format_value(self, fmt, value):
        if value is None:
            return 0.0
        if fmt == '':
            return value
        mult_pos = fmt.find('%s')
        if mult_pos > -1:
            si_unit, divisor = self.get_si_unit(value)
            fmt = fmt.replace('%s', si_unit)
            value = value/float(divisor)
        else:
            mult_pos = fmt.find('%S')
            if mult_pos > -1:
                si_unit, divisor = self.get_si_unit(value)
                fmt = fmt.replace('%S', si_unit)
                value = value/float(divisor)
        return fmt % value

    def get_si_unit(self, value):
        """ Return unit,divisor tuple for SI unit eg 2000 = k,1000 """
        for unit, divisor in SI_UNITS:
            if value >= divisor:
                return unit, divisor
        return unit, divisor

    def set_xaxis_timeformat(self, data_series):
        """
        Set the correct format for the xaxis ticks depending on
        the timespan of the supplied data series
        """
        try:
            minutes = (data_series[-1][0] - data_series[0][0]) /\
                (60000)
        except IndexError:
            format_string = '%H:%M'
            tick_interval = 1
        else:
            for min_minutes, format_string, tick_interval in TICK_INTERVALS:
                if min_minutes > minutes:
                    break
        self.parent.options['axes']['xaxis'].update({
            'renderer': twc.js_symbol('$.jqplot.DateAxisRenderer'),
            'tickOptions': {'formatString': format_string},
            'tickInterval': tick_interval * 60,
        })


class GraphWidget(JQPlotWidget):
    id = 'graph-widget'
    attribute_id = None
    graph_type_id = None
    preset_time = None
    _format = None

    def __init__(self):
        self.end_time = int(time.time())
        self.start_time = self.end_time - 3600
        super(GraphWidget, self).__init__()

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
        self._format = self._get_format()
        if self._format is None:
            return None
        self.options = self._format.get_options()
        #self.prepare_graph_template()
        self.data = self._format.get_data()
        self.options['title'] = self.get_title()
        self.resources.append(dateAxisRenderer_js)
        self.resources.append(barRenderer_js)
        self.resources.append(enhancedLegendRenderer_js)
        super(GraphWidget, self).prepare()

    def _get_format(self):
        """
        Return the correct format for this template
        Should be a class within this class of the form
        <name>Format
        """
        try:
            fmt = getattr(self, self.graph_type.template+'Format')
        except AttributeError:
            return None
        else:
            return fmt(self)

    def get_title(self):
        """ Create the Graph Title """
        return '{} {} - {}'.format(
            self.attribute.host.display_name,
            self.attribute.display_name,
            self.graph_type.display_name,
        )

    def prepare_graph_template(self):
        """ Setup the graph template specific options """
        # First the common options
        self.options = {
            'seriesDefaults': {
                'rendererOptions': {'fillToZero': True},
                'showMarker': False,
            },
            'series': [],
            'legend': {
                'show': True,
                'location': 's',
                'placement': 'outsideGrid',
            },
            'axes': {
                'xaxis': {
                    'renderer': twc.js_symbol('$.jqplot.DateAxisRenderer'),
                    'tickOptions': {'formatString': '%H:%M'},
                    'pad': 0,
                },
                'yaxis': {
                    'min': 0,
                    'forceTickAt0': True,
                    'autoscale': True,
                }
            }
        }

        if self.graph_type.template == 'totalarea':
            self.options['stackSeries'] = True
            #self.options['seriesColors'] = ( '#ff8800', '#00cc00')
            self.options['seriesDefaults'].update(
                {'fill': True, 'fillAndStroke': False})
        elif self.graph_type.template == 'stackedarea':
            self.options['stackSeries'] = True
            self.options['seriesDefaults'].update(
                {'fill': True, 'fillAndStroke': True})
            self.options['axes']['yaxis'].update({'max': 100})
        elif self.graph_type.template == 'multotarea':
            self.options['seriesColors'] = ('#ade7ad', '#ff8800')
            self.options['seriesDefaults'].update({'fill': True})

    ################################################
    # Graph templates
    class linesFormat(BaseFormat):
        """
        Graph that shows as many lines on the graph as there are
        RRD lines. Uses default line colour sequence
        """
        def get_options(self):
            return {
                'seriesDefaults': {
                    'rendererOptions': {'fillToZero': True},
                    'showMarker': False,
                },

                'legend': {
                    'show': True,
                    'location': 's',
                    'placement': 'outsideGrid',
                },
                'series': [],
                'axes': {
                    'xaxis': {
                        'renderer': twc.js_symbol('$.jqplot.DateAxisRenderer'),
                        'tickOptions': {'formatString': '%H:%M'},
                        'pad': 0,
                    },
                    'yaxis': {
                        'min': 0,
                        'forceTickAt0': True,
                        'autoscale': True,
                    }
                }
            }

        def get_data(self):
            """ Return the data for all the lines """
            data = []
            for line_idx, rrd_line in enumerate(
                    self.parent.graph_type.lines):

                mult_op, mult_val = self.get_mult(rrd_line)
                rrd = rrd_line.attribute_type_rrd
                rrd_values = rrd.fetch(self.parent.attribute_id,
                                       self.parent.start_time,
                                       self.parent.end_time)
                row = self.row_values(rrd_values, mult_op, mult_val)
                if row['len'] > 0:
                    data.append(row['values'])
                    self.set_series_label(
                        line_idx, rrd_line,
                        row['max'], row['sum'], row['len'],
                        row['values'][-1][1])
            self.set_xaxis_timeformat(row['values'])
            return data

    class areaFormat(BaseFormat):
        """
        Graph that shows a single line as a filled area
        """
        def get_options(self):
            return {
                'seriesDefaults': {
                    'rendererOptions': {'fillToZero': True},
                    'showMarker': False,
                    'fill': True,
                    'fillAndStroke': True,
                    'fillAlpha': 0.7,
                    #FIXME ? fill alpha?
                },
                'series': [],
                'legend': {
                    'show': True,
                    'location': 's',
                    'placement': 'outsideGrid',
                },
                'axes': {
                    'xaxis': {
                        'renderer': twc.js_symbol('$.jqplot.DateAxisRenderer'),
                        'tickOptions': {'formatString': '%H:%M'},
                        'pad': 0,
                    },
                    'yaxis': {
                        'min': 0,
                        'forceTickAt0': True,
                        'autoscale': True,
                    }
                }
            }

        def get_data(self):
            """ Return single line of data for the area """
            data = []
            rrd_line = self.parent.graph_type.lines[0]
            mult_op, mult_val = self.get_mult(rrd_line)
            rrd = rrd_line.attribute_type_rrd
            rrd_values = rrd.fetch(self.parent.attribute_id,
                                   self.parent.start_time,
                                   self.parent.end_time)
            row = self.row_values(rrd_values, mult_op, mult_val)
            if row['len'] > 0:
                data.append(row['values'])
                self.set_series_label(
                    0, rrd_line,
                    row['max'], row['sum'], row['len'],
                    row['values'][-1][1])
            self.set_xaxis_timeformat(row['values'])
            return data

    class stackedareaFormat(linesFormat):

        def get_options(self):
            return {
                'stackSeries': True,
                'seriesDefaults': {
                    #'rendererOptions': { 'fillToZero': True},
                    'showMarker': False,
                    'fill': True,
                },

                'legend': {
                    'show': True,
                    'location': 's',
                    'placement': 'outsideGrid',
                },
                'series': [],
                'axes': {
                    'xaxis': {
                        'renderer': twc.js_symbol('$.jqplot.DateAxisRenderer'),
                        'tickOptions': {'formatString': '%H:%M'},
                        'pad': 0,
                    },
                    'yaxis': {
                        'min': 0,
                        'forceTickAt0': True,
                        'autoscale': True,
                    }
                }
            }

    class inoutFormat(BaseFormat):
        """
        in/out graph showing two lines only. The first is "in" and
        is displayed as a green area. The secound is "out" and
        displayed a blue line.
        """
        def get_options(self):
            return {
                'seriesDefaults': {
                    'rendererOptions': {'fillToZero': True},
                    'showMarker': False,
                },
                'series': [
                    {
                        'color': '#00cc00',
                        'fill': True,
                        'fillAndStroke': True,
                        'fillAlpha': 0.4,
                    }, {
                        'fill': False,
                        'color': '#0000ff',
                    }
                ],
                'legend': {
                    'show': True,
                    'location': 's',
                    'placement': 'outsideGrid',
                },
                'axes': {
                    'xaxis': {
                        'renderer': twc.js_symbol('$.jqplot.DateAxisRenderer'),
                        'tickOptions': {'formatString': '%H:%M'},
                        'pad': 0,
                    },
                    'yaxis': {
                        'min': 0,
                        'forceTickAt0': True,
                        'autoscale': True,
                        'tickOptions': {
                            #'formatter': twc.js_symbol('tickFormatter')
                        },
                    }
                }
            }

        def get_data(self):
            """ Return the data for inout graph - 2 lines """
            data = []
            for line_idx in (0, 1):
                rrd_line = self.parent.graph_type.lines[line_idx]
                mult_op, mult_val = self.get_mult(rrd_line)
                rrd = rrd_line.attribute_type_rrd
                rrd_values = rrd.fetch(self.parent.attribute_id,
                                       self.parent.start_time,
                                       self.parent.end_time)
                row = self.row_values(rrd_values, mult_op, mult_val)
                if row['len'] > 0:
                    data.append(row['values'])
                    self.set_series_label(
                        line_idx, rrd_line,
                        row['max'], row['sum'], row['len'],
                        row['values'][-1][1])
            self.set_xaxis_timeformat(row['values'])
            return data

    class ufareaFormat(BaseFormat):
        """ Stacked area of used and free, total is calculated """
        def get_options(self):
            return {
                'seriesColors': ('#ff8800', '#00cc00', '#ff0000'),
                'stackSeries': True,
                'seriesDefaults': {
                    'rendererOptions': {'fillToZero': True},
                    'showMarker': False,
                    'fill': True,
                    'fillAndStroke': False,
                    'shadow': False,
                },

                'legend': {
                    'show': True,
                    'location': 's',
                    'placement': 'outsideGrid',
                },
                'series': [{}, {}, {
                    'fill': False,
                    'disableStack': True, }, ],
                'axes': {
                    'xaxis': {
                        'renderer': twc.js_symbol('$.jqplot.DateAxisRenderer'),
                        'tickOptions': {'formatString': '%H:%M'},
                        'pad': 0,
                    },
                    'yaxis': {
                        'min': 0,
                        'forceTickAt0': True,
                        'autoscale': True,
                    }
                }
            }

        def get_data(self):
            """ Return used,free and total for the area
            total is calculated
            """
            rrd_lines = []
            used_row = {'max': 0, 'sum': 0, 'len': 0, 'values': []}
            free_row = {'max': 0, 'sum': 0, 'len': 0, 'values': []}
            total_row = {'max': 0, 'sum': 0, 'len': 0, 'values': []}
            for line_idx in (0, 1):
                rrd_line = self.parent.graph_type.lines[line_idx]
                mult_op, mult_val = self.get_mult(rrd_line)
                rrd_lines.append({
                    'rrd_line': rrd_line,
                    'mult_op': mult_op,
                    'mult_val': mult_val,
                    'values': rrd_line.attribute_type_rrd.
                    fetch(self.parent.attribute_id,
                          self.parent.start_time,
                          self.parent.end_time),
                })

            start_time, end_time, step = rrd_lines[0]['values'][0]
            val_time = start_time
            for idx, used_values in enumerate(rrd_lines[0]['values'][2]):
                try:
                    free_values = rrd_lines[1]['values'][2][idx]
                except IndexError:
                    continue
                if used_values[0] is None or free_values[0] is None:
                    continue
                self.update_row(used_row, val_time, used_values[0])
                self.update_row(free_row, val_time, free_values[0])
                self.update_row(total_row, val_time,
                                free_values[0]+used_values[0])
                val_time += step
            self.set_series_label(
                0, rrd_lines[0]['rrd_line'],
                used_row['max'], used_row['sum'],
                used_row['len'], used_row['values'][-1][1])
            self.set_series_label(
                1, rrd_lines[1]['rrd_line'],
                free_row['max'], free_row['sum'],
                free_row['len'], free_row['values'][-1][1])
            self.set_series_label(
                2, rrd_lines[1]['rrd_line'],
                total_row['max'], total_row['sum'],
                total_row['len'], total_row['values'][-1][1],
                rrd_lines[1]['rrd_line'].legend.replace(
                    'Free', 'Total')
            )

            self.set_xaxis_timeformat(total_row['values'])
            return [used_row['values'], free_row['values'],
                    total_row['values']]

    class mtuareaFormat(ufareaFormat):
        """
        Graph that shows a two calculated lines as green/orange area
        RRDs are multiplier, total, used
        """

        def get_data(self):
            """ Return two data rows of data for the area """
            rrd_line_values = []
            used_row = {'max': 0, 'sum': 0, 'len': 0, 'values': []}
            free_row = {'max': 0, 'sum': 0, 'len': 0, 'values': []}
            total_row = {'max': 0, 'sum': 0, 'len': 0, 'values': []}
            for line_idx in (0, 1, 2):
                rrd_line = self.parent.graph_type.lines[line_idx]
                mult_op, mult_val = self.get_mult(rrd_line)
                rrd = rrd_line.attribute_type_rrd
                row_values = rrd.fetch(
                    self.parent.attribute_id,
                    self.parent.start_time,
                    self.parent.end_time)
                rrd_line_values.append({
                    'mult_op': mult_op,
                    'mult_val': mult_val,
                    'rrd_line': rrd_line,
                    'values': row_values,
                })
            start_time, end_time, step = rrd_line_values[0]['values'][0]
            val_time = start_time
            for idx, raw_multiplier in enumerate(
                    rrd_line_values[0]['values'][2]):
                if raw_multiplier[0] is None:
                    continue
                try:
                    raw_total = rrd_line_values[1]['values'][2][idx][0]
                    raw_used = rrd_line_values[2]['values'][2][idx][0]
                except IndexError:
                    continue  # skip this one

                if rrd_line_values[0]['mult_op'] is None:
                    multiplier = raw_multiplier[0]
                else:
                    multiplier = rrd_line_values[0]['mult_op'](
                        raw_multiplier[0],
                        rrd_line_values[0]['mult_val'])

                if rrd_line_values[1]['mult_op'] is None:
                    total = raw_total * multiplier
                else:
                    total = rrd_line_values[1]['mult_op'](
                        raw_total,
                        rrd_line_values[1]['mult_val']) *\
                        multiplier

                if rrd_line_values[2]['mult_op'] is None:
                    used = raw_used * multiplier
                else:
                    used = rrd_line_values[2]['mult_op'](
                        raw_used,
                        rrd_line_values[2]['mult_val']) *\
                        multiplier

                free = max(total - used, 0.0)
                self.update_row(used_row, val_time, used)
                self.update_row(free_row, val_time, free)
                self.update_row(total_row, val_time, total)
                val_time += step
            data = (used_row['values'], free_row['values'],
                    total_row['values'])

            rows = (
                (0, 2, used_row),
                (1, 0, free_row),
                (2, 1, total_row))
            for idx, lvn, row in rows:
                try:
                    last_value = row[-1][1]
                except KeyError:
                    last_value = None
                self.set_series_label(
                    idx, rrd_line_values[lvn]['rrd_line'],
                    row['max'], row['sum'], row['len'],
                    last_value)
            self.set_xaxis_timeformat(total_row['values'])
            return data
