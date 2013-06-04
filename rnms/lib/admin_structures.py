
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

from rnms import model
from structures import base_table as bt

class base_table(bt):
    def __actions__(self, obj):
        primary_fields = self.__provider__.get_primary_fields(self.__entity__)
        pklist = '/'.join(map(lambda x: str(getattr(obj, x)), primary_fields))
        value = ('<form class="inline" method="POST" action="{0}">'+\
                '<a class="btn btn-mini btn-primary" href="{0}/edit">'+\
                '<input type="hidden" name="_method" value="DELETE" />'\
                '<i title="Edit" class="icon-pencil icon-white"></i></a>'+\
                '<button title="Delete" type="submit" value="delete" class="btn btn-mini btn-warning" '+\
                'onclick="return confirm(\'Are you sure?\');"'+\
                'value="" type="submit">'+\
                '<i class="icon-trash"></i></button></form>').\
                format(pklist,) 
        return value

class attribute(base_table):
    __grid_id__ = 'attributes-grid'
    __entity__ = model.Attribute
    __limit_fields__ = ('id', 'host', 'attribute_type', 'display_name',) 

class attribute_type(base_table):
    __grid_id__ = 'attribute_types-grid'
    __entity__ = model.AttributeType
    __limit_fields__ = ('id', 'display_name', 'ad_validate', 'ad_enabled',
            'ad_command', 'ad_parameters', 'default_poller_set') 
    __headers__ = {'id': 'ID',  'display_name': 'Attribute Type', 
            'ad_validate': 'Validate in A/D', 'ad_enabled': 'A/D Enabled',
            'ad_command': 'Discovery Command', 
            'ad_parameters': 'Discovery Parameters',
            }

class backend(base_table):
    __grid_id__ = 'backends-grid'
    __entity__ = model.Backend
    __limit_fields__ = ('id', 'display_name', 'command', 'parameters')
    __headers__ = {'id': 'ID', 'display_name': 'Backend Name',}
    __column_widths__ = {'id': 30, 'display_name': 150, 'parameters': 250,}

class event_state(base_table):
    __grid_id__ = 'event_state-grid'
    __entity__ = model.EventState
    __limit_fields__ = ('id', 'display_name', 'priority', 'internal_state', )

class event_type(base_table):
    __grid_id__ = 'event_type-grid'
    __entity__ = model.EventType
    __limit_fields__ = ('id', 'display_name', 'tag', )

class group(base_table):
    __grid_id__ = 'groups-grid'
    __entity__ = model.Group
    __limit_fields__ = ('group_id', 'group_name', 'display_name',)
    __headers__ = { 'group_id': 'ID', 'display_name': 'Description',
                   'group_name': 'Group Name'}

class host(base_table):
    __grid_id__ = 'hosts-grid'
    __entity__ = model.Host
    __limit_fields__ = ('id', 'display_name', 'zone', 'mgmt_address',
                        'snmp_community', )

class poller(base_table):
    __grid_id__ = 'pollers-grid'
    __entity__ = model.Poller
    __limit_fields__ = ('id', 'display_name', 'command', 'field', 'parameters')
    __headers__ = {'id': 'ID', 'display_name': 'Poller Name',}
    __column_widths__ = {'id': 30, 'display_name': 150, 'parameters': 250,}

class poller_set(base_table):
    __grid_id__ = 'pollersets-grid'
    __entity__ = model.PollerSet
    __limit_fields__ = ('id', 'display_name', 'attribute_type')
    __headers__ = {'id': 'ID', 'display_name': 'Poller Set Name',
            'attribute_type': 'Attribute Type'}
    __column_widths__ = {'id': 30, 'display_name': 150,
            'attribute_type': 150}

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
