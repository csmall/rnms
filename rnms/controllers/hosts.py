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
from tg import expose, config, validate, flash
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates
from tw2.jqplugins import portlets
import tw2.core as twc
import tw2.forms as twf
from tw2.jqplugins.ui import set_ui_theme_name
from formencode import validators

# project specific imports
from rnms.lib.base import BaseController
from rnms.widgets import AttributeGrid,EventsWidget
from rnms.model import DBSession, metadata, Host, SNMPEnterprise, SNMPEnterprise

set_ui_theme_name(config['ui_theme'])
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
        itemmap = {'width':170}
        db_hosts = DBSession.query(Host)
        hosts = []
        for db_host in db_hosts:
            hosts.append({'title':db_host.display_name})
        return dict(itemmap=itemmap, items=hosts)


    @expose('rnms.templates.host')
    @validate(validators={'h':validators.Int()})
    def _default(self, h, *args, **kwargs):
        host = Host.by_id(h)
        if host is None:
            flash('Host ID#{} not found'.format(h), 'error')
            return {}
        else:
            vendor,devmodel = SNMPEnterprise.oid2name(host.sysobjid)
            return dict(host=host, vendor=vendor, devmodel=devmodel, zone=host.zone.display_name)
    def _idefault(self, *args):
        host_id = int(args[0])
        class LayoutWidget(portlets.ColumnLayout):
            id = 'host-layout'
            class col1(portlets.Column):
                width= '30%'
                class por1(portlets.Portlet):
                    title = 'Host Details'
                    widget = HostDetails()
                    widget.host_id = host_id
            class col2(portlets.Column):
                width= '70%'
                class por2(portlets.Portlet):
                    title = 'Host Attributes'
                    widget = AttributeGrid()
                    widget.host_id = host_id
                    widget.options['rowNum'] = 5
                    widget.options['rowList'] = [5]
                    widget.options['width'] = '100%'
            class por2(portlets.Portlet):
                title = 'Host Events'
                widget = EventsWidget
                widget.host = host_id
        return dict(layoutwidget=LayoutWidget)
