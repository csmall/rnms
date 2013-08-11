# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012-2013 Craig Small <csmall@enc.com.au>
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
""" Events Widgets """
from tw2.jqplugins.jqgrid import jqGridWidget, SQLAjqGridWidget
from tw2.jqplugins.jqgrid.base import word_wrap_css

from rnms import model
from rnms.lib import structures
from rnms.lib.table import jqGridTableBase

class EventGrid(structures.event, jqGridTableBase):
    __url__ = '/events/griddata'
    __grid_id__ = 'events-grid'
    __caption__ = 'Events'
    

class EventWidget(SQLAjqGridWidget):
    entity = model.Event
    options = {
            'url': '/events/jqgridsqla',
            'rowNum': 15,
            'viewrecords': True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'height': 'auto',
            'pager': 'event-list-pager'
            }

    def prepare(self):
        self.resources.append(word_wrap_css)
        super(EventWidget, self).prepare()

class EventsWidget2(jqGridWidget):
    def prepare(self):
        self.resources.append(word_wrap_css)
        super(EventsWidget2, self).prepare()
    options = {
            'pager': 'event-list-pager2',
            'url': '/events/jqgrid',
            'datatype': 'json',
            'postData' : { 'Foo': 'bar', },
            'colNames': ['Date', 'Type', 'Host & Zone', 'Description'],
            'colModel': [
                {
                    'name': 'Date',
                    'width': 100,
                    'align': 'right',
                }, {
                    'name': 'Type',
                    'width': '50',
                },{
                    'name': 'Host & Zone',
                    'width': 100,
                },{
                    'name': 'Description',
                    'width': 600,
                    },
                ],
            'rowNum': 15,
            'rowList': [15, 30, 50],
            'viewrecords': True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'height': 'auto',
            }
    pager_options = { 'search': True, 'refresh': True, 'add': False, }
    prmFilter = {'stringResult': True, 'searchOnEnter': False }
