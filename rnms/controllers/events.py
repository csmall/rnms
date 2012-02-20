# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011 Craig Small <csmall@enc.com.au>
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
"""Sample controller module"""
import datetime
from sqlalchemy import select,func

# turbogears imports
from tg import expose, tmpl_context
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates
from sprox.dojo.tablebase import DojoTableBase as TableBase
from sprox.dojo.fillerbase import DojoTableFiller as TableFiller

# project specific imports
from rnms.lib.base import BaseController
from rnms.model import DBSession, metadata, Event, EventSeverity,EventType
from rnms.widgets import LogPlot,RRDWidget

class EventTableFiller(TableFiller):
    __model__ = Event

event_filler = EventTableFiller(DBSession)

class EventTable(TableBase):
    __model__ = Event
    __omit_fields__ = ['event_id', '__actions__']
    __url__ = "/events/blah.json"

event_table = EventTable(DBSession)

def recursive_update(d1, d2):
      """ Little helper function that does what d1.update(d2) does,
      but works nice and recursively with dicts of dicts of dicts.
   
      It's not necessarily very efficient.
      """
   
      for k in d1.keys():
          if k not in d2:
              continue
   
          if isinstance(d1[k], dict) and isinstance(d2[k], dict):
              d1[k] = recursive_update(d1[k], d2[k])
          else:
              d1[k] = d2[k]
   
      for k in d2.keys():
          if k not in d1:
              d1[k] = d2[k]
   
      return d1


class EventsController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()
    
    @expose('rnms.templates.severitycss', content_type='text/css')
    def severitycss(self):
        severities = DBSession.query(EventSeverity)
        return dict(
                severities=severities,
                )

    @expose('rnms.templates.events')
    def index(self, **named):
        events = DBSession.query(Event).order_by(Event.id.desc())
        from webhelpers import paginate
        count = events.count()
        page = int(named.get('page', '1'))
        span = int(named.get('span', '20'))
        currentPage = paginate.Page(
                events, page, item_count=count,
                items_per_page=span,
                )
        events = currentPage.items
        return dict(
                page='index',
                events=events,
                currentPage=currentPage,
                )

    @expose('json')
    def blah(self):
        now = datetime.datetime.now()
        severities = DBSession.query(select([EventType.display_name, func.count(Event.event_type_id)],Event.event_type_id==EventType.id).group_by(Event.event_type_id))
        series = []
        ticks = []
        for severity,scount in severities:
            series.append(scount)
            ticks.append(severity)
        data= [series]
        options = { 'title': 'Type of Events',
                'axes': { 'xaxis' : {
                    'ticks': ticks }}}
        return(dict(data=data, options=options))

    @expose('rnms.templates.event_chart')
    def chart(self):
        rrdwidget = RRDWidget()
        rrdwidget.rrd_filenames = [
                '/var/local/jffnms-website/rrd/interface-2731-0.rrd'
                ]
        rrdwidget.start = (datetime.datetime.today() - datetime.timedelta(1))
        jqplot_params = self.blah()
        plotwidget = LogPlot(data=jqplot_params['data'])
        plotwidget.options = recursive_update(
                plotwidget.options, jqplot_params['options'])
        return dict(page='graph', plotwidget=plotwidget, rrdwidget=rrdwidget)

    @expose('rnms.templates.event_detail')
    def _default(self, *args):
        event_id = int(args[0])
        event = DBSession.query(Event).filter(Event.id==event_id).first()
        attribs=[('Host', event.host.display_name),
                ('Attribute', event.attribute.display_name),
                ('Alarm State', event.alarm_state.display_name),
                ('Text', event.text()),
                ('Created', event.created)]
        return dict(item_id=event.id,
                item_type='Event',
                attribs=attribs)

    @expose('rnms.templates.event_sprox')
    def test2(self):
        tmpl_context.widget = event_table
        value = event_filler.get_value(dict(limit=10))
        return dict(value=value)

    @expose('rnms.templates.events_get_one')
    def get_one(self):
        tmpl_context.widget = event_table
        value = event_filler.get_value(dict(limit=10))
        return dict(value=value)
