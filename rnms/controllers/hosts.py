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
""" Hosts controller """

# turbogears imports
from tg import expose, validate, flash, tmpl_context, url, request
from tg.decorators import require

# third party imports
from formencode import validators

# project specific imports
from rnms.lib import permissions
from rnms.lib.table import DiscoveryFiller
from rnms.lib.base import BaseTableController
from rnms.model import DBSession, Host, Event, Attribute
from rnms.widgets import MainMenu, HostMap,\
        BootstrapTable, EventTable, HostDetails, AttributeStateDoughnut
from rnms.widgets.attribute import DiscoveredAttsGrid
from rnms.widgets.panel_tile import PanelTile


class HostsController(BaseTableController):
    allow_only = permissions.host_ro

    @expose('rnms.templates.host.index')
    @validate(validators={'z': validators.Int(min=1)})
    def index(self, z=None, *args, **kw):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        if z is not None:
            table_filter = {'z': z}
        else:
            table_filter = {}

        class HostTile(PanelTile):
            title = 'Host List'
            fullwidth = True

            class MyTable(BootstrapTable):
                data_url = url('/hosts/tabledata.json')
                columns = [('id', 'ID'),
                           ('display_name', 'Name'),
                           ('mgmt_address', 'Management Address')]
                filter_params = table_filter
                detail_url = url('/hosts/')

        return dict(page='host', hosttable=HostTile())

    @expose('json')
    @validate(validators={
        'z': validators.Int(min=1),
        'offset': validators.Int(min=0),
        'limit': validators.Int(min=1)})
    def tabledata(self, **kw):
        """ Provides the JSON data for the standard bootstrap table
        """
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}

        conditions = []
        if kw['z'] is not None:
            conditions.append(Host.zone_id == kw['z'])
        table_data = self._get_tabledata(Host, conditions=conditions, **kw)
        if table_data is None:
            return {}
        rows = [
                {'id': row.id,
                 'display_name': row.display_name,
                 'mgmt_address': row.mgmt_address}
                for row in table_data[1]]
        return dict(total=table_data[0], rows=rows)

    @expose('json')
    @validate(validators={'h': validators.Int(min=1)})
    @require(permissions.host_rw)
    def griddiscover(self, **kw):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        filler = DiscoveryFiller()
        return filler.get_value(**kw)

    @expose('rnms.templates.host.detail')
    @validate(validators={'h': validators.Int(min=1)})
    def _default(self, h):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='host', main_menu=MainMenu)
        host = Host.by_id(h)
        if host is None:
            flash('Host ID#{} not found'.format(h), 'error')
            return dict(page='host', main_menu=MainMenu)
        vendor, devmodel = host.snmp_type()
        highest_alarm = Event.host_alarm(host.id)
        if highest_alarm is None:
            host_state = 'Up'
        else:
            host_state = highest_alarm.event_state.display_name.capitalize()

        thehost = host

        class HostDetailPanel(PanelTile):
            title = 'Host Details'

            class MyHostDetails(HostDetails):
                host = thehost
                extra = {'host_state': host_state,
                         'vendor': vendor,
                         'devmodel': devmodel,
                         }

        class AttributeStatusPanel(PanelTile):
            title = 'Attribute Status'

            class AttributeStatus(AttributeStateDoughnut):
                host_id = h

        class HostEventPanel(PanelTile):
            title = 'Events for ' + host.display_name
            fullwidth = True

            class HostEventTable(EventTable):
                filter_params = {'h': h}

        class AttributesPanel(PanelTile):
            title = 'Host Attributes'

            class AttributesTable(BootstrapTable):
                data_url = url('/attributes/namelist.json', {'h': h})
                detail_url = url('/attributes/')
                columns = [('display_name', 'Name'), ]
                sort_name = 'display_name'
                fit_panel = True

        return dict(page='host',
                    details_panel=HostDetailPanel(),
                    status_panel=AttributeStatusPanel(),
                    attributes_panel=AttributesPanel(),
                    host=host,
                    events_panel=HostEventPanel)

    @expose('rnms.templates.host.map')
    @validate(validators={
        'z': validators.Int(min=1), 'events': validators.Bool(),
        'alarmed': validators.Bool()})
    def map(self, z=None, events=False, alarmed=False, **kw):
        """ Display a map of the Hosts, optionally filtered by Zone id
        and optionally showing events for those hosts
        """
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='host', main_menu=MainMenu)

        class HostMapTile(PanelTile):
            title = 'Host Map'
            fullwidth = True

            class HostMap2(HostMap):
                zone_id = z
                alarmed_only = (alarmed == 1)

        if events:
            class HostEventTile(PanelTile):
                title = 'Host Events'
                fullwidth = True

                class HostEventTable(EventTable):
                    filter_params = {'z': z}
            events_panel = HostEventTile()
        else:
            events_panel = None

        return dict(page='hosts', main_menu=MainMenu,
                    host_map=HostMapTile(), events_panel=events_panel)

    @expose('rnms.templates.host.discover')
    @validate(validators={'h': validators.Int(min=2)})
    def discover(self, h):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return dict(page='host', main_menu=MainMenu)
        w = DiscoveredAttsGrid()
        edit_url = url('/attributes/add_disc', {'h': h})
        return dict(page='host', main_menu=MainMenu,
                    w=w, edit_url=edit_url,
                    griddata={'h': h})

    @expose('rnms.templates.widgets.select')
    def option(self):
        """ Return a list of hosts. If user has required
        permission it shows all, else just their ones """
        if permissions.host_ro:
            hosts = DBSession.query(Host.id, Host.display_name)
        else:
            hosts = DBSession.query(Host.id, Host.display_name).filter(
                Host.id.in_(
                    DBSession.query(Attribute.host_id).filter(
                        Attribute.user_id == request.identity['user'].user_id)
                )
            )
        items = hosts.all()
        items.insert(0, ('', '-- Choose Host --'))
        return dict(items=items)
