
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
"""
 This file holds the table structures, which are inherited by TableBase or
 FillerBase objects, that are used in the admin system.  For objects outside
 the admin system, put them into the structures file.
"""
import tg

from rnms import model
from structures import base_table as bt


def click(model_name, mod_id, name):
    return '<a href="{}">{}</a>'.format(
        tg.url('/admin/{}/{}/edit'.format(model_name, mod_id)),
        name)


class base_table(bt):
    @property
    def __url__(self):
        url = tg.request.path_url
        if url[-1] == '/':
            url = url[:-1]
        return url + '.json'

    def action_buttons(self, obj):
        """ Returns primary fields and default buttons as a list """
        primary_fields = self.__provider__.get_primary_fields(self.__entity__)
        pklist = '/'.join(map(lambda x: str(getattr(obj, x)), primary_fields))
        buttons = [
            ('<a class="delete-confirm btn btn-mini btn-primary"'
             'href="{0}/edit">'
             '<i title="Edit" class="icon-pencil icon-white"></i></a>').
            format(pklist, ),
            ('<a class="delete-confirm btn btn-mini btn-danger href="{0}"'
             'onclick="del_confirm({0})">'
             '<i title="Delete" class="icon-trash icon-white">'
             '</i></a>').format(pklist)
        ]
        return buttons

    def __actions__(self, obj):
        return ''.join(
            ['<div class="action_buttons">'] +
            self.action_buttons(obj) +
            ['</div>'])


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


class group(base_table):
    __grid_id__ = 'groups-grid'
    __entity__ = model.Group
    __limit_fields__ = ('group_id', 'group_name', 'display_name',)
    __headers__ = {'group_id': 'ID', 'display_name': 'Description',
                   'group_name': 'Group Name'}


class host(base_table):
    __grid_id__ = 'hosts-grid'
    __entity__ = model.Host
    __limit_fields__ = ('id', 'display_name', 'zone', 'mgmt_address',
                        )

    def action_buttons(self, obj):
        return [
            ('<a class="btn btn-mini btn-info" href="{0}">'
             '<i title="Show Attributes for host" '
             'class="icon-list icon-white"></i></a>').
            format(tg.url('/admin/attributes/', {'h': obj.id})),
            ('<a class="btn btn-mini btn-warning" href="{0}">'
             '<i title="Discover Attributes" '
             'class="icon-eye-open icon-white"></i></a>').
            format(tg.url('/hosts/discover/{0}'.format(obj.id))),
        ] + super(host, self).action_buttons(obj)


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
        ] + self.action_buttons(obj)
