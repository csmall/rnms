
# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012-2014 Craig Small <csmall@enc.com.au>
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
"""
 This file holds the table structures, which are inherited by TableBase or
 FillerBase objects, that are used in the admin system.  For objects outside
 the admin system, put them into the structures file.
"""
from markupsafe import Markup
import tg
from tg.i18n import lazy_ugettext as l_
from tgext.admin.layouts import BootstrapAdminTableFiller

from rnms import model
from rnms.widgets.button import Button
from structures import base_table as bt


def click(model_name, mod_id, name):
    return Markup('<a href="{}">{}</a>'.format(
        tg.url('/admin/{}/{}/edit'.format(model_name, mod_id)),
        name))


class TableFiller(BootstrapAdminTableFiller):

    def __actions__(self, obj):
        # This is from tgext.admin.widgets
        actions = super(TableFiller, self).__actions__(obj)
        if hasattr(self, 'extra_actions'):
            return actions + self.extra_actions(obj)
        return actions

    def host(self, obj):
        """ Format host """
        return click('hosts', obj.host_id, obj.host.display_name)


class base_table(bt):
    @property
    def i__url__(self):
        url = tg.request.path_url
        if url[-1] == '/':
            url = url[:-1]
        return url + '.json'


class attribute(base_table):
    __entity__ = model.Attribute
    __limit_fields__ = ('id', 'host', 'attribute_type', 'display_name',)


class attribute_field(base_table):
    __entity__ = model.AttributeField
    __limit_fields__ = ('id', 'attribute', 'attribute_type_field', 'value')


class attribute_type(base_table):
    __entity__ = model.AttributeType
    __limit_fields__ = (
        'id', 'display_name', 'ad_validate', 'ad_enabled',
        'default_poller_set')
    __headers__ = {
        'id': 'ID',  'display_name': 'Attribute Type',
        'ad_validate': 'Validate in A/D', 'ad_enabled': 'A/D Enabled',
        'default_poller_set': 'Default Poller Set',
        }

    def action_buttons(self, obj):
        return [
            ('<a class="btn btn-mini btn-info" href="{0}">'
             '<i title="Show Graph Types" '
             'class="icon-picture icon-white"></i></a>').
            format(tg.url('/admin/graphtypes/', {'at': obj.id})),
            ('<a class="btn btn-mini btn-info" href="{0}">'
             '<i title="Show RRDs" '
             'class="icon-folder-close icon-white"></i></a>').
            format(tg.url('/admin/attributetyperrds/',
                          {'at': obj.id})),
        ] + super(attribute_type, self).action_buttons(obj)


class attribute_type_rrd(base_table):
    __entity__ = model.AttributeTypeRRD
    __limit_fields__ = ('id', 'attribute_type', 'position', 'display_name')


class autodiscovery_policy(base_table):
    __grid_id__ = 'adpolicies-grid'
    __entity__ = model.AutodiscoveryPolicy
    __limit_fields__ = ('id', 'display_name')


class backend(base_table):
    __grid_id__ = 'backends-grid'
    __entity__ = model.Backend
    __limit_fields__ = ('id', 'display_name', 'command', 'parameters')
    __headers__ = {'id': 'ID', 'display_name': 'Backend Name'}
    __column_widths__ = {'id': 30, 'display_name': 150, 'parameters': 250}


class event_state(base_table):
    __grid_id__ = 'event_state-grid'
    __entity__ = model.EventState
    __limit_fields__ = ('id', 'display_name', 'priority', 'internal_state', )


class event_type(base_table):
    __grid_id__ = 'event_type-grid'
    __entity__ = model.EventType
    __limit_fields__ = ('id', 'display_name', 'tag')


class graph_type(base_table):
    __entity__ = model.GraphType
    __limit_fields__ = ('id', 'display_name', 'attribute_type',
                        'template')


class graph_type_line(base_table):
    __grid_id__ = 'graph_type_line-grid'
    __entity__ = model.GraphTypeLine
    __limit_fields__ = ('id', 'position', 'attribute_type_rrd',
                        'multiplier')
    __default_sort__ = 'position'


class group(base_table):
    __grid_id__ = 'groups-grid'
    __entity__ = model.Group
    __limit_fields__ = ('group_id', 'group_name', 'display_name',)
    __headers__ = {'group_id': 'ID', 'display_name': 'Description',
                   'group_name': 'Group Name'}


class host(base_table):
    __entity__ = model.Host
    __limit_fields__ = ('id', 'display_name', 'zone', 'mgmt_address',
                        )

    def extra_actions(self, obj):
        return Button(tg.url('/admin/attributes/', {'host_id': obj.id}),
                      'list', 'info',
                      tooltip='Show all Attributes for this host') +\
            Button(tg.url('/hosts/discover/'+str(obj.id)),
                   'eye-open', 'info',
                   tooltip='Discover Attributes for this host')
        return [
            ('<a class="btn btn-mini btn-info" href="{0}">'
             '<i title="Show Attributes for host" '
             'class="icon-list icon-white"></i></a>').
            format(tg.url('/admin/attributes/', {'h': obj.id})),
            ('<a class="btn btn-mini btn-warning" href="{0}">'
             '<i title="Discover Attributes" '
             'class="icon-eye-open icon-white"></i></a>').
            format(tg.url('/hosts/discover/{0}'.format(obj.id))),
        ]


class logfile(base_table):
    __grid_id__ = 'logfiles-grid'
    __entity__ = model.Logfile
    __limit_fields__ = ('id', 'display_name', 'pathname', 'polled',
                        'logmatchset')
    __headers__ = {'polled': 'Last Polled', 'logmatchset': 'Match Set'}

    def logmatchset(self, obj):
        return click('logmatchsets', obj.logmatchset_id,
                     obj.logmatchset.display_name)


class logmatchset(base_table):
    __grid_id__ = 'logmatchsets-grid'
    __entity__ = model.LogmatchSet


class logmatchrow(base_table):
    __grid_id__ = 'logmatchrows-grid'
    __entity__ = model.LogmatchRow
    __limit_fields__ = ('id', 'logmatch_set', 'position', 'match_text',
                        'event_type')
    __column_widths__ = {'__actions__': 50, 'id': 20, 'logmatch_set': 50,
                         'position': 20, 'event_type': 50}


class permission(base_table):
    pass


class poller(base_table):
    __entity__ = model.Poller
    __limit_fields__ = ('id', 'display_name', 'command', 'field', 'parameters')
    __headers__ = {'id': 'ID', 'display_name': 'Poller Name'}
    __column_widths__ = {'id': 30, 'display_name': 150, 'parameters': 250}


class poller_set(base_table):
    __entity__ = model.PollerSet
    __limit_fields__ = ('id', 'display_name', 'attribute_type')
    __headers__ = {'id': 'ID', 'display_name': 'Poller Set Name',
                   'attribute_type': 'Attribute Type'}
    __column_widths__ = {'id': 30, 'display_name': 150,
                         'attribute_type': 150}

    def action_buttons(self, obj):
        return [
            ('<a class="btn btn-mini btn-info" href="{0}">'
             '<i title="Show rows for Poller Set" '
             'class="icon-list icon-white"></i></a>').format(
                tg.url('/admin/pollerrows/', {'ps': obj.id}))
        ] + super(poller_set, self).action_buttons(obj)


class poller_row(base_table):
    __entity__ = model.PollerRow
    __limit_fields__ = ('position', 'poller_set', 'poller', 'backend')
    __default_sort__ = 'position'


class severity(base_table):
    __grid_id__ = 'severity-grid'
    __entity__ = model.Severity
    __limit_fields__ = ('id', 'display_name', 'fgcolor', 'bgcolor', )
    __headers__ = {'id': 'ID', 'display_name': 'Severity',
                   'fgcolor': 'Foreground', 'bgcolor': 'Background'}


class snmp_device(base_table):
    __entity__ = model.SNMPDevice
    __limit_fields__ = ('id', 'enterprise', 'display_name', 'oid')


class snmp_enterprise(base_table):
    __entity__ = model.SNMPEnterprise
    __limit_fields__ = ('id', 'display_name')
    __headers__ = {'id': 'ID', 'display_name': 'Enterprise Name'}

    def extra_actions(self, obj):
        return Markup('''
    <a href="/admin/snmpdevices/?enterprise_id={}" class="btn btn-primary"
       title="Show Devices for {} Enterprise">
      <span class="glyphicon glyphicon-list"></span>
    </a>'''.format(obj.id, obj.display_name))


class trigger(base_table):
    __limit_fields__ = ('id', 'display_name', 'email_owner', 'email_users')


class user(base_table):
    __entity__ = model.User
    __xml_fields__ = ('groups',)
    __limit_fields__ = ('user_id', 'display_name', 'user_name',
                        'created', 'groups')


class zone(base_table):
    __grid_id__ = 'zones-grid'
    __entity__ = model.Zone
    __limit_fields__ = ('id', 'display_name', 'short_name',)

    def action_buttons(self, obj):
        return [
            ('<a class="btn btn-mini btn-info" href="{0}">'
             '<i title="Show Hosts in zone"'
             'class="icon-list icon-white"></i></a>').format(
                tg.url('/admin/hosts/', {'z': obj.id}))
        ] + super(zone, self).action_buttons(obj)
