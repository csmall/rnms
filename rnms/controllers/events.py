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
"""Sample controller module"""
import datetime
import math
from sqlalchemy import select,func,or_
from sqlalchemy.orm import subqueryload, subqueryload_all, contains_eager
from formencode import validators

# turbogears imports
from tg import expose, tmpl_context, request
import tg
from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates
from tw2.jqplugins import portlets
import tw2.core as twc
import tw2.forms as twf
#import tw2.jqplugins.jqgrid


# project specific imports
from rnms.lib.base import BaseController
from rnms.model import DBSession, metadata, Event, EventSeverity,EventType, Host
from rnms.widgets.event import EventsWidget, EventsWidget2

class EventsController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()
    
    @expose('rnms.templates.host')
    def index(self, *args, **kwargs): 
        class LayoutWidget(portlets.ColumnLayout):
            id = 'event-layout'
            class por1(portlets.Portlet):
                title = 'Events'
                widget = EventsWidget2
        return dict(layoutwidget=LayoutWidget)

    @expose('rnms.templates.host')
    def oldindex(self, *args): 
        class LayoutWidget(portlets.ColumnLayout):
            id = 'event-layout'
            class por1(portlets.Portlet):
                title = 'Events'
                widget = EventsWidget
        return dict(layoutwidget=LayoutWidget)

    @expose('json')
    def jqgridsqla(self, *args, **kwargs):
        return EventsWidget.request(request).body

    @expose('json')
    def jqgrid(self, page=1, rows=30, sidx=1, soid='asc', _search='false',
            searchOper=u'', searchField=u'', searchString=u'', **kw):

        import logging
        logging.info(kw)
        qry = DBSession.query(Event)
        qry = qry.filter()
        qry = qry.order_by()
        result_count = qry.count()
        rows = int(rows)

        offset = (int(page)-1) * rows
        qry = qry.offset(offset).limit(rows)
        qry.options(subqueryload(Event.event_type), contains_eager(Event.fields), subqueryload_all('attribute.fields.attribute_type_field'), subqueryload(Event.host))

        records = [{'id': rw,
            'cell': [ rw.created.strftime('%d %b %H:%M:%S'), '<div class="severity{0}">{1}</div>'.format(rw.event_type.severity_id, rw.event_type.display_name), rw.host.display_name, rw.text()]} for rw in qry]
        total = int(math.ceil(result_count / float(rows)))
        return dict(page=int(page), total=total, records=result_count, rows=records)

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

    @expose('json')
    @validate(validators={'page':validators.Int()})
    def griddata(self, page=1, rows=30, sidx=1, soid='asc', _search='false',
            searchOper=u'', searchField=u'', searchString=u'', **kw):

        qry = DBSession.query(Event)
        qry = qry.filter()
        qry = qry.order_by()
        result_count = qry.count()

        offset = (page-1) * rows
        qry = qry.offset(offset).limit(rows)

        records = [{'id': rw.id,
                'cell': [ rw.id, rw.host, rw.created]} for rw in qry]
        total = int(ceil(result_count / float(rows)))
        return dict(page=page, total=total, records=result_count, rows=records)


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

