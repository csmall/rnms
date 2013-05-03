# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012,2013 Craig Small <csmall@enc.com.au>
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
""" Event controller module"""
import math
from sqlalchemy import and_
from sqlalchemy.orm import subqueryload, subqueryload_all, contains_eager
from formencode import validators

# turbogears imports
from tg import expose, url
from tg import validate

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates

# project specific imports
from rnms.lib.base import BaseController
from rnms.model import DBSession, Event, Severity,EventType, Host,Attribute
from rnms.widgets.event import EventsGrid
from rnms.lib.jsonquery import json_query

class EventsController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()

    @expose('rnms.templates.event_index')
    @validate(validators={'a':validators.Int(), 'h':validators.Int()})
    def index(self, a=None, h=None):

        w = EventsGrid()
        w.attribute_id = a
        w.host_id = h

        return dict(w=w)

    @expose('rnms.templates.event_index')
    @validate(validators={'a':validators.Int()})

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
        severities = DBSession.query(Severity)
        return dict(
                severities=severities,
                )

    @expose('rnms.templates.mapseveritycss', content_type='text/css')
    def mapseveritycss(self):
        severities = DBSession.query(Severity)
        return dict(
                severities=[(s.id, s.bgcolor, '%.6x'%(int(s.bgcolor,16) & 0xfefefe >> 1)) for s in severities],
                )


    @expose('json')
    @validate(validators={'page':validators.Int(), 'rows':validators.Int(),
                          'sidx':validators.String(),
                          'sord':validators.String(),
                          '_search':validators.String(),
                          'searchOper':validators.String(),
                          'searchField':validators.String(),
                          'searchString':validators.String(),
                          'h':validators.Int(), 'a':validators.Int(),
                          'z':validators.Int()})
    def griddata(self, page, rows, sidx, sord, _search='false', searchOper=u'',
                 searchField=u'', searchString=u'', h=None, a=None, z=None, **kw):

        conditions = []
        if h is not None:
            conditions.append(Event.host_id == h)
        if a is not None:
            conditions.append(Event.attribute_id == a)
        if z is not None:
            conditions.append(Host.zone_id == z)

        qry = DBSession.query(Event).join(Event.event_type,
                                          Event.attribute).join(Host).filter(and_(*conditions))
        colnames = (('created', Event.created), ('event_type', EventType.display_name), ('host_display_name', Host.display_name), ('attribute', Attribute.display_name), ('event_description', None))

        result_count, qry = json_query(qry, colnames, page, rows, sidx, sord, _search=='true', searchOper, searchField, searchString)

        records = [{'id': rw.id,
                'cell': self.format_gridrow(rw.event_type.severity_id, (
                    (rw.created, None),
                    (rw.alarm_state.display_name, None),
                    (rw.event_type.display_name, None),
                    (rw.host.display_name, url('/hosts/'+str(rw.host_id))),
                    (rw.attribute.display_name, url('/attributes/'+str(rw.attribute_id))),
                    (rw.text(), None)
                    ))} for rw in qry]
        return dict(page=page, total=result_count, records=result_count, rows=records)

    def format_gridrow(self, sev_id, cells):
        """ Returned the cells formated with the severity ID """
        retvals = []
        for text,curl in cells:
            if curl is not None:
                retvals.append('<div class="severity{}"><a href="{}">{}</a></div>'.format(sev_id, curl, text))
            else:
                retvals.append('<div class="severity{}">{}</div>'.format(sev_id, text))
        return retvals

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

