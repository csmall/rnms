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
from tg import expose, url, validate, flash, tmpl_context
from sqlalchemy import and_

# third party imports
from formencode import validators

# project specific imports
from rnms.lib import states, structures
from rnms.lib.base import BaseGridController
from rnms.lib.jsonquery import json_query
from rnms.model import DBSession, Attribute, AttributeType, Host
from rnms.widgets import AttributeSummary, AttributeMap,\
        AttributeStatusPie, AttributesGrid, EventsGrid, InfoBox
from rnms.widgets.graph import GraphWidget
from rnms.lib.table import jqGridTableFiller

class AttributesController(BaseGridController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()

    @expose('rnms.templates.attribute_index')
    @validate(validators={'h':validators.Int(min=1)})
    def index(self, h=None, *args, **kw):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        agrid = AttributesGrid()
        agrid.host_id = h
        return dict(w=agrid, page='attribute')

    @expose('rnms.templates.attribute_detail')
    @validate(validators={'a':validators.Int(min=1)})
    def _default(self, a):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        attribute = Attribute.by_id(a)
        if attribute is None:
            flash('Attribute ID#{} not found'.format(a), 'error')
            return {}
        detailsbox = InfoBox()
        detailsbox.title = 'Attribute Details'
        events_grid = EventsGrid()
        events_grid.attribute_id = a

        graph_type = attribute.attribute_type.get_graph_type()
        if graph_type is None:
            print 'no graph'
            graphbox = None
        else:
            gw = GraphWidget()
            gw.id = 'graph-widget-{}'.format(a)
            gw.attribute = attribute
            gw.graph_type = graph_type
            graphbox = InfoBox()
            graphbox.title = graph_type.title(attribute)
            graphbox.child_widget = gw

            more_url = url('/graphs',{'a':a})

        return dict(page='attribute', attribute=attribute,
                    detailsbox=detailsbox, eventsgrid=events_grid,
                    more_url=more_url,
                    graphbox=graphbox)

    @expose('rnms.templates.attribute_map')
    @validate(validators={'h':validators.Int(min=1), 'events':validators.Bool(),
                          'alarmed':validators.Bool()})
    def map(self, h=None, events=False, alarmed=False):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        amap = AttributeMap()
        amap.host_id = h
        amap.alarmed_only = alarmed
        if events == True:
            eventsbox = InfoBox()
            eventsbox.title = 'Attribute Events'
            eventsbox.child_widget = EventsGrid()
            eventsbox.child_widget.host_id = h
        else:
            eventsbox = None
        return dict(page='attributes', attribute_map=amap, eventsbox=eventsbox)

    @expose('json')
    def minigriddata(self, **kw):
        class AttFiller(structures.attribute_mini, jqGridTableFiller):
            pass
        return super(AttributesController, self).griddata(
            AttFiller,
            {'h': validators.Int(min=1)}, **kw)

    @expose('json')
    def griddata(self, *args, **kw):
        class AttFiller(structures.attribute, jqGridTableFiller):
            def oper_state(self, obj):
                return 'hello'
        return super(AttributesController, self).griddata(
            AttFiller,
            {'h': validators.Int(min=1)}, **kw)

    @expose('json')
    @validate(validators={'h': validators.Int(), 'page':validators.Int(), 'rows':validators.Int(), 'sidx':validators.String(), 'sord':validators.String(), '_search':validators.String(), 'searchOper':validators.String(), 'searchField':validators.String(), 'searchString':validators.String()})
    def griddata_old(self, page, rows, sidx, sord, _search='false',
                 searchOper='', searchField='', searchString='', h=None,
                 **kw):
        conditions = []
        if tmpl_context.form_errors:
            return dict(errors={
                k:str(v) for k,v in tmpl_context.form_errors.items()})
        if h is not None:
            conditions.append(Attribute.host_id == int(h))
        qry = DBSession.query(Attribute).\
                join(Attribute.attribute_type,
                     Attribute.host).filter(and_(*conditions))
        colnames = (
            ('host', Host.display_name),
            ('display_name', Attribute.display_name),
            ('attribute_type', AttributeType.display_name),
            ('description', None),
            ('oper_state', None),
            ('admin_state', None),
        )
        result_count, qry = json_query(qry, colnames, page, rows, sidx,
                                       sord, _search=='true', searchOper,
                                       searchField, searchString)
        records = [{'id': rw.id,
                    'cell': (
                        '<a href="{}">{}</a>'.format(
                            url('/hosts/'+str(rw.host.id)),
                            rw.host.display_name),
                        '<a href="{}">{}</a>'.format(
                            url('/attributes/'+str(rw.id)),
                            rw.display_name),
                        rw.attribute_type.display_name,
                        rw.description(),
                        rw.oper_state_name(),
                        rw.admin_state_name()
                    )} for rw in qry]
        return dict(page='attributes', total=result_count,
                    records=result_count, rows=records)


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

