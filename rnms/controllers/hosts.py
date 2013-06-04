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
""" Hosts controller """

# turbogears imports
from tg import expose, validate, flash,tmpl_context, url
from tg.decorators import require

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates
import tw2.forms as twf
from formencode import validators

# project specific imports
from rnms.lib import structures
from rnms.lib import permissions
from rnms.lib.table import jqGridTableFiller, DiscoveryFiller
from rnms.lib.base import BaseGridController
from rnms.model import DBSession, Host, Event
from rnms.widgets import InfoBox
from rnms.widgets.host import HostMap, HostsGrid
from rnms.widgets.attribute import MiniAttributesGrid, DiscoveredAttsGrid
from rnms.widgets.event import EventsGrid


class HostDetails(twf.TableLayout):
    """
    Returns a TableLayout Widget showing host details
    """
    hostname = twf.LabelField(value='Host not found')
    ip_address = twf.LabelField(id='IP_Address', value='Unknown')
    zone = twf.LabelField(value='Unknown')
    snmp_sysobjid = twf.LabelField(value='Unknown')
    def prepare(self):
        twf.TableLayout.prepare(self)
        host = DBSession.query(Host).filter(Host.id==self.host_id).first()
        if host is not None:
            self.children[0].value = host.display_name
            self.children[1].value = host.mgmt_address
            self.children[2].value = host.zone.display_name
            self.children[3].value = host.sysobjid + "ff"


class HostsController(BaseGridController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()
    allow_only = permissions.host_ro

    @expose('rnms.templates.host_index')
    def index(self):
        w = HostsGrid()
        return dict(w=w, page='host')

    @expose('json')
    def griddata(self, **kw):
        class HostFiller(structures.host, jqGridTableFiller):
            pass
        return super(HostsController, self).griddata(HostFiller, {}, **kw)
    @expose('json')
    def gridindex(self, **kw):
        class HostFiller(structures.host_list, jqGridTableFiller):
            pass
        return super(HostsController, self).griddata(HostFiller, {}, **kw)

    @expose('json')
    @validate(validators={'h':validators.Int(min=1)})
    @require(permissions.host_rw)
    def griddiscover(self, **kw):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        filler = DiscoveryFiller()
        return filler.get_value(**kw)

    @expose('rnms.templates.host')
    @validate(validators={'h':validators.Int(min=1)})
    def _default(self, h):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        host = Host.by_id(h)
        if host is None:
            flash('Host ID#{} not found'.format(h), 'error')
            return {}
        vendor,devmodel = host.snmp_type()
        highest_alarm = Event.host_alarm(host.id)
        if highest_alarm is  None:
            host_state = 'Up'
        else:
            host_state = highest_alarm.event_state.display_name.capitalize()

        detailsbox = InfoBox()
        detailsbox.title = 'Host Details'
        attributes_grid = MiniAttributesGrid()
        attributes_grid.host_id = h
        events_grid = EventsGrid()
        events_grid.host_id = h
        return dict(host=host, vendor=vendor, devmodel=devmodel,
                    host_state=host_state,
                    attributes_grid=attributes_grid,
                    detailsbox=detailsbox,
                    events_grid=events_grid)

    @expose('rnms.templates.host_map')
    @validate(validators={
        'z':validators.Int(min=1),'events':validators.Bool(),
                          'alarmed': validators.Bool()})
    def map(self, z=None, events=False, alarmed=False):
        """ Display a map of the Hosts, optionally filtered by Zone id
        and optionally showing events for those hosts
        """
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        hmap = HostMap()
        hmap.zone_id = z
        hmap.alarmed_only = alarmed
        if events == True:
            eventsbox = InfoBox()
            eventsbox.title = 'Host Events'
            eventsbox.child_widget = EventsGrid()
            eventsbox.child_widget.zone_id = z
        else:
            eventsbox = None
        return dict(page='hosts', host_map=hmap, eventsbox=eventsbox)

    @expose('rnms.templates.host_discover')
    @validate(validators={'h':validators.Int(min=2)})
    def discover(self, h):
        if tmpl_context.form_errors:
            self.process_form_errors()
            return {}
        w = DiscoveredAttsGrid()
        w.host_id = h
        edit_url = url('/attributes/add_disc', {'h':h})
        return dict(w=w, page='host', edit_url=edit_url)
