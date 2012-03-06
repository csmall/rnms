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
from sqlalchemy import select,func,or_

# turbogears imports
from tg import expose, tmpl_context
import tg
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates
import tw2.core as twc
import tw2.jqplugins.jqgrid


# project specific imports
from rnms.lib.base import BaseController
from rnms.model import DBSession, metadata, Event, EventSeverity,EventType
from rnms.widgets import LogPlot,RRDWidget

class EventsWidget(twc.Widget):
    template = 'rnms.templates.eventswidget'

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

class GridWidget(tw2.jqplugins.jqgrid.jqGridWidget):
    id = 'grid_widget'
    entity = Event
    excluded_columns = ['id']
    prmFilter = {'stringResult': True, 'searchOnEnter': False}
    pager_options = { "search" : True, "refresh" : True, "add" : False, }

    options = {
            'pager': 'event-grid_pager',
    #        'url': '/tw2_controllers/db_jqgrid/',
            'colNames':[ 'Date', 'Type', 'Host', 'Description'],
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
            'url' : '/events/griddata',
            'rowNum':15,
            'rowList':[15,30,50],
            'viewrecords':True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'width': 900,
            'height': 'auto',
            }



class EventsController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()
    
    @expose('rnms.templates.severitycss', content_type='text/css')
    def severitycss(self):
        severities = DBSession.query(EventSeverity)
        return dict(
                severities=severities,
                )

    @expose('rnms.templates.widget')
    def test3(self, *args, **kw):
        myw = EventsWidget()
        from webhelpers import paginate
        conditions = []
        copy_args=[]
        if 't' in kw:
            conditions.append(Event.event_type_id==kw['t'])
            copy_args.append('t')
        if 'h' in kw:
            conditions.append(Event.host_id==kw['h'])
            copy_args.append('h')

        condition = or_(*conditions)
        events = DBSession.query(Event).filter(condition).order_by(Event.id.desc())
        count = events.count()
        page = int(kw.get('page', '1'))
        span = int(kw.get('span', '20'))
        myw.currentPage = paginate.Page(
                events, page, item_count=count,
                items_per_page=span,
                )
        for arg in copy_args:
            myw.currentPage.kwargs[arg] = str(kw[arg])
        
        myw.events = myw.currentPage.items
        myw.tgurl = tg.url
        return dict(widget=myw, page='attribute')

    @expose('rnms.templates.events')
    def index(self, **named):
        from webhelpers import paginate
        conditions = []
        copy_args=[]
        if 'type' in named:
            conditions.append(Event.event_type_id==named['type'])
            copy_args.append('type')
        if 'host_id' in named:
            conditions.append(Event.host_id==named['host_id'])
            copy_args.append('host_id')

        condition = or_(*conditions)
        events = DBSession.query(Event).filter(condition).order_by(Event.id.desc())
        count = events.count()
        page = int(named.get('page', '1'))
        span = int(named.get('span', '20'))
        currentPage = paginate.Page(
                events, page, item_count=count,
                items_per_page=span,
                )
        for arg in copy_args:
            currentPage.kwargs[arg] = str(named[arg])
        
        events = currentPage.items
        return dict(
               page='events',
               events=events,
               currentPage=currentPage,
               )

    @expose('json')
    def griddata(self):
        events =DBSession.query(Event)
        data=[]
        for event in events:
            data.append({'created': event.created,})
        return dict(data=data)


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

    @expose('rnms.templates.events_get_one')
    def get_one(self):
        tmpl_context.widget = event_table
        value = event_filler.get_value(dict(limit=10))
        return dict(value=value)

    @expose('rnms.templates.widget')
    def grid(self, *args, **kw):
        mw = twc.core.request_local()['middleware']
        mw.controllers.register(GridWidget, 'db_jqgrid')
        return dict(widget=GridWidget, page='events')

