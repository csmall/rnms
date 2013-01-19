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
""" RRD Graphs """
import logging
import time
from base64 import b64encode

import rrdtool

from tg import tmpl_context, flash, url

from tw2 import forms as twf
import tw2.core as twc

from rnms import model
from rnms.lib.parsers import fill_fields

logger = logging.getLogger('rnms')

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
        try:
            attribute_id = tmpl_context.form_values['a']
        except KeyError:
            attribute = None
        else:
            attribute = model.Attribute.by_id(attribute_id)

        if attribute is None:
            flash('No attribute given')
            self.options = ()
        else:
            self.options = tuple((gt.id,gt.display_name) for gt in model.DBSession.query(model.GraphType).filter(model.GraphType.attribute_type == attribute.attribute_type))
            try:
                self.value = tmpl_context.form_values['gt']
            except KeyError:
                pass
        super(GraphTypeSelector, self).prepare()


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
        try:
            graphv = rrdtool.graphv('-', graph_options + graph_definition)
        except TypeError as errmsg:
            flash('RRDTool error: {}'.format(errmsg))
        else:
            self.create_legend(graphv)
            self.img_data = b64encode(graphv['image'])
            self.img_width = graphv['image_width']
            self.img_height = graphv['image_height']

    def prepare(self):
        self.get_graphv()
        if self.graph_type.title != '':
            self.title = ' '.join((self.attribute.host.display_name, self.attribute.display_name, fill_fields(self.graph_type.title, attribute=self.attribute)))
        else:
            self.title = ' '.join((self.attribute.host.display_name, self.attribute.display_name, self.graph_type.display_name))
        self.tg_url = url

        super(GraphWidget, self).prepare
