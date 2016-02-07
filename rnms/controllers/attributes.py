# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2016 Craig Small <csmall@enc.com.au>
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

# turbogears imports
from tg import expose, url, validate, flash, tmpl_context, predicates, request

# third party imports
from formencode import validators, ForEach

# project specific imports
from rnms.lib import structures, permissions
from rnms.lib.base import BaseTableController
from rnms.model import DBSession, Attribute, Host
from rnms.widgets import AttributeMap,\
    EventTable, InfoBox,\
    MainMenu, BootstrapTable, PanelTile,\
    AttributeDetails, LineChart
from rnms.widgets.graph import GraphWidget
from rnms.lib.table import jqGridTableFiller


class AttributesController(BaseTableController):
    # Uncomment this line if your controller requires an authenticated user
    allow_only = predicates.not_anonymous()

    @expose('rnms.templates.attribute.index')
    @validate(validators={'h': validators.Int(min=1)})
    def index(self, h=None, *args, **kw):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='attribute', main_menu=MainMenu)
        if h is not None:
            table_filter = {'h': h}
        else:
            table_filter = {}

        class AttributeTile(PanelTile):
            title = 'Attribute List'
            fullwidth = True
            fullheight = True

            class AttributeTable(BootstrapTable):
                data_url = url('/attributes/tabledata.json')
                columns = [('id', 'ID'),
                           ('host', 'Host'),
                           ('display_name', 'Name'),
                           ('attribute_type', 'Attribute Type'),
                           ('owner', 'Owner'),
                           ('created', 'Created')]
                filter_params = table_filter
                detail_url = url('/attributes/')
        return dict(page='attribute', attributetable=AttributeTile())

    @expose('json')
    @validate(validators={
        'h': validators.Int(min=1),
        'offset': validators.Int(min=0),
        'limit': validators.Int(min=1)})
    def tabledata(self, h=None, **kw):
        """ Provides the JSON data for the standard bootstrap table
        """
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}

        conditions = []
        if h is not None:
            conditions.append(Attribute.host_id == h)
        table_data = self._get_tabledata(Attribute,
                                         conditions=conditions, **kw)
        if table_data is None:
            return {}
        rows = [
                {'id': row.id,
                 'host': row.host.display_name if row.host else '-',
                 'display_name': row.display_name,
                 'attribute_type': row.attribute_type.display_name if
                 row.attribute_type else '-',
                 'owner': row.user.display_name if row.user else '-',
                 'created': row.created}
                for row in table_data[1]]
        return dict(total=table_data[0], rows=rows)

    @expose('json')
    @validate(validators={
        'h': validators.Int(min=1),
        'offset': validators.Int(min=0),
        'limit': validators.Int(min=1)})
    def namelist(self, h=None, **kw):
        """ Provides list of attribute names for given host
        """
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}

        conditions = []
        if h is not None:
            conditions.append(Attribute.host_id == h)
        table_data = self._get_tabledata(Attribute,
                                         conditions=conditions, **kw)
        if table_data is None:
            return {}
        rows = [
                {'id': row.id,
                 'display_name': row.display_name}
                for row in table_data[1]]
        return dict(total=table_data[0], rows=rows)

    @expose('rnms.templates.attribute.detail')
    @validate(validators={'a': validators.Int(min=1)})
    def _default(self, a):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='attribute', main_menu=MainMenu)
        attribute = Attribute.by_id(a)
        if attribute is None:
            flash('Attribute ID#{} not found'.format(a), 'error')
            return dict(page='attribute', main_menu=MainMenu)
        this_attribute = attribute

        class DetailsPanel(PanelTile):
            title = 'Attribute Details'

            class MyAttributeDetails(AttributeDetails):
                attribute = this_attribute

        class GraphPanel(PanelTile):
            title = 'Graphs'

            class AttributeChart(LineChart):
                attribute_id = a
                data_url='fixme'

        class EventsPanel(PanelTile):
            title = 'Events for {} - {}'.format(
                attribute.host.display_name, attribute.display_name)
            fullwidth = True

            class AttributeEvents(EventTable):
                filter_params = {'a': a}

        graph_type = attribute.attribute_type.get_graph_type()
        if graph_type is None:
            graphbox = None
            more_url = None
        else:
            class MyGraph(GraphWidget):
                id = 'graph-{}-{}'.format(a, graph_type.id)
                attribute_id = a
                graph_type_id = graph_type.id
            gw = MyGraph()
            graphbox = InfoBox()
            graphbox.title = graph_type.formatted_title(attribute)
            graphbox.child_widget = gw

            more_url = url('/graphs', {'a': a})

        return dict(page='attribute',
                    attribute=attribute,
                    attribute_id=a,
                    details_panel=DetailsPanel(),
                    graph_panel=GraphPanel(),
                    eventsgrid=EventsPanel(),
                    more_url=more_url,
                    graphbox=graphbox)

    @expose('rnms.templates.attribute.map')
    @validate(validators={
        'h': validators.Int(min=1),
        'events': validators.Bool(),
        'alarmed': validators.Bool()})
    def map(self, h=None, events=False, alarmed=False):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='attribute', main_menu=MainMenu)
        amap = AttributeMap()
        amap.host_id = h
        amap.alarmed_only = alarmed
        if events:
            if h is not None:
                table_filter = {'h': h}
            else:
                table_filter = {}

            class HostEventTile(PanelTile):
                title = 'Host Events'
                fullwidth = True

                class HostEventTable(EventTable):
                    filter_params = table_filter
            events_panel = HostEventTile()
        else:
            events_panel = None
        return dict(page='attribute', main_menu=MainMenu,
                    attribute_map=amap, events_panel=events_panel)

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
            pass
        return super(AttributesController, self).griddata(
            AttFiller,
            {'h': validators.Int(min=1)}, **kw)

    @expose('rnms.templates.widgets.select')
    @validate(validators={'h': validators.Int(min=1), 'a':
                          ForEach(validators.Int(min=1))})
    def option(self, h=None, a=[], **kw):
        if not tmpl_context.form_errors:
            conditions = []
            atts = []
            if not permissions.host_ro:
                conditions.append(
                    Attribute.user_id == request.identity['user'].user_id
                )
            if h is not None:
                try:
                    conditions.append(Attribute.host_id == h)
                except:
                    pass
            if a != []:
                try:
                    conditions.append(Attribute.id.in_(a))
                except:
                    pass
            rows = DBSession.query(
                Attribute.id, Attribute.attribute_type_id,
                Host.display_name, Attribute.display_name).\
                select_from(Attribute).join(Host).filter(*conditions)
            atts = [(row[0], ' - '.join(row[2:]), row[1]) for row in rows]
        return dict(data_name='atype', items=atts)
