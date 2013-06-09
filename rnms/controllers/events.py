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
#import math
#from sqlalchemy.orm import subqueryload, subqueryload_all, contains_eager
from formencode import validators

# turbogears imports
from tg import expose, tmpl_context, validate

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates
from tg.predicates import has_permission

# project specific imports
from rnms.lib.base import BaseGridController
from rnms.model import DBSession, Severity,EventType
from rnms.widgets import EventsGrid, MainMenu
from rnms.lib.table import jqGridTableFiller
from rnms.lib import structures

class EventsController(BaseGridController):
    allow_only = has_permission('manage')
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()


    @expose('rnms.templates.event_index')
    @validate(validators={'a':validators.Int(min=1),
                          'h':validators.Int(min=1)})
    def index(self, a=None, h=None):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='event', main_menu=MainMenu)

        w = EventsGrid()
        w.attribute_id = a
        w.host_id = h
        return dict(page='event', main_menu=MainMenu,
                    w=w)

    @expose('rnms.templates.severitycss', content_type='text/css')
    def severitycss(self):
        severities = DBSession.query(Severity)
        return {'severities':severities}

    @expose('rnms.templates.mapseveritycss', content_type='text/css')
    def mapseveritycss(self):
        severities = DBSession.query(Severity)
        return dict(
                severities=[(s.id, s.bgcolor, '%.6x'%(int(s.bgcolor,16) & 0xfefefe >> 1)) for s in severities],
                )


    @expose('json')
    def griddata(self, **kw):
        class EventFiller(structures.event, jqGridTableFiller):
            pass
        return super(EventsController, self).griddata(EventFiller, {}, **kw)

    @expose('rnms.templates.widgets.select')
    def type_option(self):
        types = DBSession.query(EventType.id, EventType.display_name)
        return dict(items=types)
