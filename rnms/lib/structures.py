# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
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
from rnms import model
from tg import url

def click(model_name, mod_id, name):
    return '<a href="{}">{}</a>'.format(
            url('/{}/{}'.format(model_name, mod_id)),
            name)

class base_table(object):
    __headers__ = {
        'id': 'ID',
        'display_name': 'Name', 'host': 'Host',
        'attribute_type': 'Attribute Type',
        'admin_state': 'Admin State', 
        'event_type': 'Event Type',
        'user': 'Owner',
    }

    def created(self, obj):
        return obj.created.strftime('%Y-%b-%d %H:%M:%S')


class attribute(base_table):
    __entity__ = model.Attribute
    __limit_fields__ = ('id', 'host', 'display_name', 'attribute_type',
                        'user','created')
    __omit_fields__ = ('__actions__',)
    def display_name(self,obj):
        return click('attributes',obj.id, obj.display_name)
    def host(self, obj):
        if obj.host is None:
            return ''
        return click('hosts', obj.host_id, obj.host.display_name)

class attribute_mini(base_table):
    __entity__ = model.Attribute
    __hide_primary_field__ = True
    __omit_fields__ = ('__actions__',)
    __limit_fields__ = ('id', 'attribute_type', 'display_name', 'user')

    def attribute_type(self, obj):
        return click('attributes',obj.id, obj.attribute_type.display_name)
    def display_name(self,obj):
        return click('attributes',obj.id, obj.display_name)

class host(base_table):
    __entity__ = model.Host
    __limit_fields__ = ('id', 'display_name', 'zone', 'created')
    __omit_fields__ = ('__actions__',)
    __column_widths__ = {'id': 30, 'created':140}

    def zone(self, obj):
        return click('zones', obj.zone_id, obj.zone.display_name)
    def display_name(self, obj):
        return '<a href="{}">{}</a>'.format(
            url('/hosts/{}'.format(obj.id)),
            obj.display_name)

class host_list(host):
    """ Used for viewing not editing a host list """
    __hide_primary_field__ = True
    __omit_fields__ = ('__actions__',)

class zone(base_table):
    __entity__ = model.Zone
    __limit_fields__ = ('id', 'display_name', 'short_name')

class event(base_table):
    __entity__ = model.Event
    __hide_primary_field__ = True
    __omit_fields__ = ('__actions__',)
    __limit_fields__ = ('id', 'created', 'host', 'attribute',
                        'event_type', 'description' )
    __column_widths__ = {'created': 140, 'event_type': 80, 'description': 500}

    def host(self, obj):
        if obj.host is None:
            return ''
        return '<a href="{}">{}</a>'.format(
            url('/hosts/{}'.format(obj.host_id)),
            obj.host.display_name)
    def attribute(self, obj):
        if obj.attribute is None:
            return ''
        return '<a href="{}">{}</a>'.format(
            url('/attributes/{}'.format(obj.attribute_id)),
            obj.attribute.display_name)
    def event_type(self, obj):
        try:
            return '<div class="severity{} event_type_td">{}</div>'.format(
                obj.event_state.severity_id,
                obj.event_type.display_name)
        except AttributeError:
            return ''


    def description(self, obj):
        return obj.text()
