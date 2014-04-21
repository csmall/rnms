
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
    return '<a href="{}">{}</a>'.format(
        tg.url('/admin/{}/{}/edit'.format(model_name, mod_id)),
        name)


class TableFiller(BootstrapAdminTableFiller):
    def __actions__(self, obj):
        # This is from tgext.admin.widgets
        primary_fields = self.__provider__.get_primary_fields(self.__entity__)
        pklist = '/'.join(map(lambda x: str(getattr(obj, x)), primary_fields))
        actions = Markup('''
    <a href="%(pklist)s/edit" class="btn btn-primary">
        <span class="glyphicon glyphicon-pencil"></span>
    </a>
    <div class="hidden-lg hidden-md">&nbsp;</div>
    <form method="POST" action="%(pklist)s" style="display: inline">
        <input type="hidden" name="_method" value="DELETE" />
        <button type="submit" class="btn btn-danger"
         onclick="return confirm('%(msg)s')">
            <span class="glyphicon glyphicon-trash"></span>
        </button>
    </form>
''' % dict(msg=l_('Are you sure?'),
           pklist=pklist))

        try:
            return actions + self.extra_actions(obj)
        except AttributeError:
            return actions


class base_table(bt):
    @property
    def i__url__(self):
        url = tg.request.path_url
        if url[-1] == '/':
            url = url[:-1]
        return url + '.json'


class attribute(base_table):
    __grid_id__ = 'attributes-grid'
    __entity__ = model.Attribute
    __limit_fields__ = ('id', 'host', 'attribute_type', 'display_name',)


class attribute_type(base_table):
    __grid_id__ = 'attribute_types-grid'
    __entity__ = model.AttributeType
    __limit_fields__ = (
        'id', 'display_name', 'ad_validate', 'ad_enabled',
        'ad_command', 'ad_parameters', 'default_poller_set')
    __headers__ = {
        'id': 'ID',  'display_name': 'Attribute Type',
        'ad_validate': 'Validate in A/D', 'ad_enabled': 'A/D Enabled',
        'ad_command': 'Discovery Command',
        'ad_parameters': 'Discovery Parameters',
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
    __grid_id__ = 'attribute_type_rrds-grid'
    __entity__ = model.AttributeTypeRRD


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
    __grid_id__ = 'graph_type-grid'
    __entity__ = model.GraphType
    __limit_fields__ = ('id', 'display_name', 'attribute_type',
                        'template')

    def action_buttons(self, obj):
        return [
            ('<a class="btn btn-mini btn-info" href="{0}">'
             '<i title="Show Lines" '
             'class="icon-list icon-white"></i></a>').
            format(tg.url('/admin/graphtypelines/', {'gt': obj.id})),
            ('<a class="btn btn-mini btn-info" href="{0}">'
             '<i title="Show RRDs" '
             'class="icon-folder-close icon-white"></i></a>').
            format(tg.url('/admin/attributetyperrds/',
                          {'at': obj.attribute_type_id})),
        ] + super(graph_type, self).action_buttons(obj)


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
        return Button(
            tg.url('/admin/attributes/', {'h': obj.id}),
            'list', 'info')
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


class poller(base_table):
    __grid_id__ = 'pollers-grid'
    __entity__ = model.Poller
    __limit_fields__ = ('id', 'display_name', 'command', 'field', 'parameters')
    __headers__ = {'id': 'ID', 'display_name': 'Poller Name'}
    __column_widths__ = {'id': 30, 'display_name': 150, 'parameters': 250}


class poller_set(base_table):
    __grid_id__ = 'pollersets-grid'
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
    __grid_id__ = 'pollerrows-grid'
    __entity__ = model.PollerRow
    __limit_fields__ = ('position', 'poller_set', 'poller', 'backend')
    __default_sort__ = 'position'

    def poller_set(self, obj):
        return click('pollersets', obj.poller_set_id,
                     obj.poller_set.display_name)

    def poller(self, obj):
        return click('pollers', obj.poller_id,
                     obj.poller.display_name)


class severity(base_table):
    __grid_id__ = 'severity-grid'
    __entity__ = model.Severity
    __limit_fields__ = ('id', 'display_name', 'fgcolor', 'bgcolor', )
    __headers__ = {'id': 'ID', 'display_name': 'Severity',
                   'fgcolor': 'Foreground', 'bgcolor': 'Background'}


class user(base_table):
    __grid_id__ = 'users-grid'
    __entity__ = model.User
    __limit_fields__ = ('user_id', 'display_name', 'user_name',
                        'created',)


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
