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
from tg import expose, validate, flash,url, tmpl_context

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates
import tw2.forms as twf
from formencode import validators

# project specific imports
from rnms.lib.base import BaseController
from rnms.widgets import AttributeSummary, InfoBox
from rnms.widgets.host import HostsGrid, HostMap
from rnms.model import DBSession, Host, Zone, Event
from rnms.lib.jsonquery import json_query
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


class HostsController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()

    @expose('rnms.templates.host_index')
    def index(self):
        w = HostsGrid()
        return dict(w=w)

    @expose('json')
    @validate(validators={'page':validators.Int(), 'rows':validators.Int(), 'sidx':validators.String(), 'sord':validators.String(), '_search':validators.String(), 'searchOper':validators.String(), 'searchField':validators.String(), 'searchString':validators.String()})
    def griddata(self, page, rows, sidx, sord, _search='false', searchOper='', searchField='', searchString='', **kw):

        qry = DBSession.query(Host).join(Host.zone)
        colnames = (('display_name',Host.display_name),('zone_display_name',Zone.display_name))
        result_count, qry = json_query(qry, colnames, page, rows, sidx, sord, _search=='true', searchOper, searchField, searchString)

        records = [{'id': rw.id,
            'cell': ['<a href="'+url('/hosts/'+str(rw.id))+'">'+rw.display_name+'</a>', rw.zone.display_name]} for rw in qry]
        return dict(page=int(page), total=result_count, records=result_count, rows=records)

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
            host_state = highest_alarm.alarm_state.display_name.capitalize()

        detailsbox = InfoBox()
        detailsbox.title = 'Host Details'
        attributesbox = InfoBox()
        attributesbox.title = 'Attribute Status'
        attributesbox.child_widget = AttributeSummary()
        attributesbox.child_widget.host_id = h
        eventsbox = InfoBox()
        eventsbox.title = 'Events'
        eventsbox.child_widget = EventsGrid()
        eventsbox.child_widget.host_id = h
        return dict(host=host, vendor=vendor, devmodel=devmodel,
                    host_state=host_state,
                    attributesbox=attributesbox,
                    detailsbox=detailsbox,
                    eventsbox=eventsbox)

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
