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

# turbogears imports
from tg import expose
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates

# project specific imports
from rnms.lib.base import BaseController
from rnms.model import DBSession, metadata, Event, EventSeverity


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
        events = DBSession.query(Event).order_by(Event.id)
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
