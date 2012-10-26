# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012 Craig Small <csmall@enc.com.au>
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
import tg
import tw2.core as twc
from rnms.model import DBSession, Event
from sqlalchemy import select,func,or_
from tw2.jqplugins.jqgrid import jqGridWidget, SQLAjqGridWidget
from tw2.jqplugins.jqgrid.base import word_wrap_css

from rnms import model

class EventsGrid(jqGridWidget):
    id = 'events-grid-id'
    options = {
            'pager' : 'events-grid-pager',
            'url' : '/events/griddata',
            'colNames':[ 'Date', 'Type', 'Host', 'Description'],
            'datatype' : 'json',
            'colModel' : [
                {
                    'name': 'created',
                    'width': 75,
                    'align': 'right',
                },{
                    'name': 'event_type',
                    'width': 75,
                    'align': 'right',
                },{
                    'name': 'host_display_name',
                    'width': 75,
                    'align': 'right',
                },{
                    'name': 'event_description',
                    'width': 75,
                    'align': 'left',
                },
            ],
            'viewrecords':True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'width': 900,
            'height': 'auto',
            }

class EventsWidget3(twc.Widget):
    id = 'events-widget'
    template = 'rnms.templates.eventswidget'

    host = twc.Param('Limit events by this host id')
    event_type = twc.Param('Limit events by this event_type id')

    def prepare(self):
        from webhelpers import paginate
        conditions = []
        copy_args = {}
        if hasattr(self, 'host'):
            host_id = getattr(self, 'host')
            if type(host_id) <> int:
                raise ValueError, "Host ID must be an integer"
            conditions.append(Event.host_id==host_id)
            copy_args['h']=1
        else:
            conditions.append(Event.host_id > 0)
        condition = or_(*conditions)
        events = DBSession.query(Event).filter(condition).order_by(Event.id.desc())
        #events = DBSession.query(Event).order_by(Event.id.desc())
        count = events.count()
        page = int(getattr(self, 'page', '1'))
        span = int(getattr(self, 'span', '20'))
        self.currentPage = paginate.Page(
                events, page, item_count=count,
                items_per_page=span,
                )
        #for arg in copy_args:
        #    self.currentPage.kwargs[arg] = str(kw[arg])
        
        self.events = self.currentPage.items
        self.tgurl = tg.url
        super(EventsWidget, self).prepare

class EventsWidget(SQLAjqGridWidget):
    def prepare(self):
        self.resources.append(word_wrap_css)
        super(EventsWidget, self).prepare()
    entity = model.Event
    options = {
            'url': '/events/jqgridsqla',
            'rowNum': 15,
            'viewrecords': True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'height': 'auto',
            'pager': 'event-list-pager'
            }

class EventsWidget2(jqGridWidget):
    def prepare(self):
        self.resources.append(word_wrap_css)
        super(EventsWidget2, self).prepare()
    options = {
            'pager': 'event-list-pager2',
            'url': '/events/jqgrid',
            'datatype': 'json',
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
