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
import json

# turbogears imports
from tg import expose, url, validate, flash, tmpl_context, predicates,\
    request, redirect
from tg.decorators import require

# third party imports
from formencode import validators, ForEach

# project specific imports
from rnms.lib import permissions
from rnms.lib.base import BaseTableController
from rnms.model import DBSession, Attribute, Host, AttributeType
from rnms.widgets import AttributeMap,\
    EventTable, \
    BootstrapTable, PanelTile,\
    AttributeDetails
from rnms.widgets.c3js import C3Chart
from rnms.lib.table import DiscoveryFiller


class AttributesController(BaseTableController):
    # Uncomment this line if your controller requires an authenticated user
    allow_only = predicates.not_anonymous()

    @expose('rnms.templates.attribute.index')
    @validate(validators={'h': validators.Int(min=1)})
    def index(self, h=None, *args, **kw):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='attribute')
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
            return dict(page='attribute')
        attribute = Attribute.by_id(a)
        if attribute is None:
            flash('Attribute ID#{} not found'.format(a), 'error')
            return dict(page='attribute')
        this_attribute = attribute
        this_graph_type = attribute.attribute_type.get_graph_type()
        if this_graph_type:
            graph_title = this_graph_type.formatted_title(this_attribute)
        else:
            graph_title = 'No Graph'

        class DetailsPanel(PanelTile):
            title = 'Attribute Details'

            class MyAttributeDetails(AttributeDetails):
                attribute = this_attribute

        class GraphPanel(PanelTile):
            title = graph_title
            fullheight = True
            fillrow = True

            class AttributeChart(C3Chart):
                attribute = this_attribute
                show_legend = True
                graph_type = this_graph_type
                attribute_id = a
                chart_height = 200

        class EventsPanel(PanelTile):
            title = 'Events for {} - {}'.format(
                attribute.host.display_name, attribute.display_name)
            fullwidth = True

            class AttributeEvents(EventTable):
                filter_params = {'a': a}

        return dict(page='attribute',
                    attribute=attribute,
                    attribute_id=a,
                    details_panel=DetailsPanel(),
                    graph_panel=GraphPanel(),
                    eventsgrid=EventsPanel(),
                    )

    @expose('rnms.templates.attribute.map')
    @validate(validators={
        'h': validators.Int(min=1),
        'events': validators.Bool(),
        'alarmed': validators.Bool()})
    def map(self, h=None, events=False, alarmed=False):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='attribute')
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
        return dict(page='attribute',
                    attribute_map=amap, events_panel=events_panel)

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

    @expose('rnms.templates.attribute.discover')
    @validate(validators={'h': validators.Int(min=2)})
    def discover(self, h):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='host')

        class MyTable(BootstrapTable):
            id = 'discover_table'
            have_checkbox = True
            data_url = url('/attributes/discoverdata.json', {'h': h})
            hidden_columns = ['id', 'fields', ]
            columns = [('display_name', 'Name'),
                       ('attribute_type', 'Attribute Type'),
                       ('admin_state', 'Admin State'),
                       ('oper_state', 'Oper State'),
                       ]

        return dict(discover_table=MyTable,
                    add_url=url('/attributes/bulk_add', {'h': h}))

    @expose('json')
    @validate(validators={'h': validators.Int(min=1)})
    @require(permissions.host_rw)
    def discoverdata(self, **kw):
        """ Return the discovered Attributes for the given host in a JSON
            format """
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        filler = DiscoveryFiller()
        return filler.get_value(**kw)

    @expose('rnms.template.attribute.bulk_add')
    @validate(validators={'h': validators.Int(min=2)})
    def bulk_add(self, h, attribs):
        """ From a discovery phase, add the following attributes """
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}

        host = Host.by_id(h)
        if host is None:
            flash('Unknown Host ID {}'.format(h))
            return {}

        old_att_id = None
        new_count = 0

        decoded_attribs = json.loads(attribs)
        for vals in decoded_attribs:
            if old_att_id != vals['atype_id']:
                attribute_type = AttributeType.by_id(vals['atype_id'])
                if attribute_type is None:
                    flash('Unknown Attribute Type ID {}'.
                          format(vals['atype_id']),
                          'warning')
                    return {}

            new_attribute = Attribute(
                host=host, attribute_type=attribute_type,
                display_name=vals['display_name'], index=vals['id'])
            for tag, value in vals['fields'].items():
                new_attribute.set_field(tag, value)
            DBSession.add(new_attribute)
            new_count += 1

        flash('{} Attributes added'.format(new_count), 'success')
        redirect('/attributes', params={'h': h})
