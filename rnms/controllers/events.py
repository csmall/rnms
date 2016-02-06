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
""" Event controller module"""
from formencode import validators

# turbogears imports
from tg import expose, tmpl_context, validate

# third party imports
from tg.predicates import has_permission
from sqlalchemy import extract, func

# project specific imports
from rnms.lib.base import BaseTableController
from rnms.model import DBSession, Severity, EventType, Event, EventState
from rnms.widgets import PanelTile, EventTable
from rnms.lib.table import jqGridTableFiller
from rnms.lib import structures
from rnms.lib.states import State

default_colors = ["#468847", "#F89406", "#B94A48", "#999999",
                  "#3887AD", "#222222"]


class EventsController(BaseTableController):
    allow_only = has_permission('manage')

    @expose('rnms.templates.event.index')
    @validate(validators={'a': validators.Int(min=1),
                          'h': validators.Int(min=1)})
    def index(self, a=None, h=None):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='event')

        table_filter = {}
        if a is not None:
            table_filter['a'] = a
        elif h is not None:
            table_filter['h'] = h

        class EventTile(PanelTile):
            title = 'Event List'
            fullwidth = True
            fullheight = True

            class MyEventTable(EventTable):
                filter_params = table_filter
        return dict(page='event', eventtable=EventTile())

    @expose('json')
    @validate(validators={
        'a': validators.Int(min=1),
        'h': validators.Int(min=1),
        'offset': validators.Int(min=0),
        'limit': validators.Int(min=1)})
    def tabledata(self, a=None, h=None, **kw):
        """ Provides the JSON data for the standard bootstrap table
        """
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}

        conditions = []
        if h is not None:
            conditions.append(Event.host_id == h)
        if a is not None:
            conditions.append(Event.attribute_id == a)
        table_data = self._get_tabledata(Event, conditions=conditions, **kw)
        if table_data is None:
            return {}
        rows = [
                {'id': row.id,
                 'severity': row.event_state.severity.display_name,
                 'severity_id': row.event_state.severity_id,
                 'created': row.created.strftime('%Y-%b-%d %H:%M:%S'),
                 'host': row.host.display_name,
                 'attribute': row.attribute.display_name,
                 'event_type': row.event_type.display_name,
                 'description': row.text()}
                for row in table_data[1]]
        return dict(total=table_data[0], rows=rows)

    @expose('json')
    def hourly(self):
        import datetime
        yesterday = datetime.datetime.now() - datetime.timedelta(hours=24)
        this_hour = datetime.datetime.now().hour
        hours = range(this_hour+1, 24) + range(0, this_hour+1)
        datasets = []

        for event_state in State._STATES:
            rows = DBSession.query(extract('hour', Event.created),
                                   func.count(1)).\
                group_by(extract('hour', Event.created)).\
                filter(Event.event_state_id == EventState.id).\
                filter(EventState.internal_state == event_state).\
                filter(Event.created > yesterday)
            dict_rows = dict(rows.all())
            dataset_data = []
            for hr in hours:
                try:
                    dataset_data.append(dict_rows[hr])
                except KeyError:
                    dataset_data.append(0)
            datasets.append({
                'event_state': event_state,
                'label': event_state,
                'data': dataset_data
                })
        data = {
                'labels': map('{}:00'.format, hours),
                'datasets': datasets,
                    }
        for idx, d in enumerate(data['datasets']):
            rgb_color = State(d['event_state']).rgb_color_str()
            d['fillColor'] = 'rgba({}, 0.31)'.format(rgb_color)
            d['strokeColor'] = 'rgba({}, 0.7)'.format(rgb_color)
            d['pointColor'] = 'rgba({}, 0.7)'.format(rgb_color)
            d['pointStrokeColor'] = '#fff'
            d['pointHighlightFill'] = '#fff'
        return data

    @expose('rnms.templates.event.severitycss', content_type='text/css')
    def severitycss(self):
        severities = DBSession.query(Severity)
        return {'severities': severities}

    @expose('rnms.templates.map.severitycss', content_type='text/css')
    def mapseveritycss(self):
        severities = DBSession.query(Severity)
        return dict(
            severities=[
                (s.id, s.bgcolor,
                    '%.6x' % (int(s.bgcolor, 16) & 0xfefefe >> 1))
                for s in severities],)

    @expose('json')
    def griddata(self, **kw):
        class EventFiller(structures.event, jqGridTableFiller):
            pass
        return super(EventsController, self).griddata(EventFiller, {}, **kw)

    @expose('rnms.templates.widgets.select')
    def type_option(self):
        types = DBSession.query(EventType.id, EventType.display_name)
        return dict(items=types)
