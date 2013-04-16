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
from sqlalchemy import func

# turbogears imports
from tg import expose
from tg import validate, flash
from sqlalchemy import and_

# third party imports
from formencode import validators

# project specific imports
from rnms.lib import states
from rnms.lib.base import BaseController
from rnms.widgets.attribute import AttributeSummary, AttributeMap, AttributeStatusPie
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
    def statuspie(self):
        att_states = ('up', 'alert', 'down', 'Admin Down', 'testing', 'unknown')
        att_count = { x:0 for x in att_states}
        
        down_attributes = DBSession.query(Attribute).filter(Attribute.admin_state == states.STATE_DOWN)
        att_count['Admin Down'] = down_attributes.count()

        attributes = DBSession.query(func.count(Attribute.admin_state), Attribute.admin_state).group_by(Attribute.admin_state)
        for attribute in attributes:
            try:
                state_name = states.STATE_NAMES[attribute[1]]
            except KeyError:
                pass
            else:
                att_count[state_name] = attribute[0]
        data = [
                [ [att_name.capitalize(), cnt] for (att_name,cnt) in att_count],
                ]
        pie = AttributeStatusPie(data=data)
        return dict(w=pie)

    @expose('rnms.templates.widget')
    def att_summary(self):
        w= AttributeSummary()
        return dict(widget=w)

