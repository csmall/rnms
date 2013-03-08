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
"""Attribute controller module"""
import datetime
from sqlalchemy import select,func

# turbogears imports
import tg
from tg import expose, request
from tg import redirect, validate, flash
from sqlalchemy import and_

# third party imports
import tw2.sqla
#from tg.i18n import ugettext as _
#from repoze.what import predicates
from formencode import validators
from tw2.jqplugins.ui import set_ui_theme_name
from sqlalchemy import asc

# project specific imports
from rnms.lib.base import BaseController
from rnms.widgets.attribute import AttributeSummary, AttributeMap
from rnms.model import DBSession, Attribute

class AttributesController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()
    
    #@expose('rnms.templates.widget')
    #def index(self, *args, **kw):
    #    return dict(widget=AttributeGrid2, page='attribute')
    @expose('rnms.templates.attribute')
    @validate(validators={'a':validators.Int()})
    def _default(self, a):
        attribute = Attribute.by_id(a)
        if attribute is None:
            flash('Attribute ID#{} not found'.format(a), 'error')
            return {}
        return dict(attribute=attribute)

    @expose('rnms.templates.widget')
    @validate(validators={'h':validators.Int()})
    def map(self, h=None):
        w = AttributeMap()
        w.host_id = h
        return dict(widget=w)

    @expose('json')
    @validate(validators={'hostid':validators.Int()})
    def jqsumdata(self, hostid=0, page=1, rows=1, *args, **kw):
        rows = int(rows)
        page = int(page)
        start_row = page * rows
        end_row = (page+1) * rows

        conditions = []
        if hostid > 0:
            conditions.append(Attribute.host_id == hostid)
        attributes =DBSession.query(Attribute).filter(and_(*conditions))
        row_count = attributes.count()
        data=[]
        for attribute in attributes[start_row:end_row]:
            data.append({
                'cell' : [ attribute.attribute_type.display_name,
                    attribute.display_name,
                attribute.description(),
                attribute.oper_state_name(),
                attribute.admin_state_name(),
                ],
                'id': attribute.id})
        return dict(page=page,records=row_count,total=row_count/rows, rows=data)
#    @expose('json')
    #def jqgrid(self, *args, **kwargs):
    #    return AttributeGrid2.request(request).body

    @expose('rnms.templates.widget')
    def att_summary(self):
        w= AttributeSummary()
        return dict(widget=w)

