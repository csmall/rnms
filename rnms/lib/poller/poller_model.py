# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
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
""" Private models use within the Poller engine """

import time

from rnms import model
from rnms.model import DBSession, Attribute
from rnms.lib.parsers import safe_substitute, find_field_keys

import plugins


class CachePoller(object):
    __copy_attrs__ = (
        'display_name', 'command', 'field', 'parameters')
    poller_function = None

    def __init__(self, db_poller):
        for copy_attr in self.__copy_attrs__:
            setattr(self, copy_attr, getattr(db_poller, copy_attr))

        # Load the actual function
        if self.command is not None and self.command != 'no_poller':
            try:
                self.poller_function = getattr(plugins, "poll_"+self.command)
            except AttributeError:
                raise ValueError("Poller Plugin \"{}\" not found for {}.".
                                 format(self.command, db_poller.display_name))

    def run(self, poller_row, pobj, patt, poller_buf):
        """
        Run the real poller method "poll_BLAH" based upon the command
        field for this poller.
        """
        return self.poller_function(
            poller_buf, pobj=pobj,
            attribute=patt,
            parsed_params=self.parsed_parameters(patt))

    def parsed_parameters(self, patt):
        """
        Poller.parameters may have certain fields that need to be parsed
        by filling in <item> with some value from the attribute
        """
        from rnms.model import AttributeField
        if self.parameters == '':
            return ''
        field_keys = find_field_keys(self.parameters)
        if field_keys == []:
            return self.parameters

        # Put in the easy ones
        field_values = {
            'attribute_id': patt.id,
            'host_id': patt.host_id,
            'index': patt.index,
        }
        for field_key in field_keys:
            if field_key in field_values:
                continue
            field_value = AttributeField.field_value(patt.id, field_key)
            if field_value is not None:
                field_values[field_key] = field_value
        return safe_substitute(self.parameters, field_values)


class CacheHost(object):
    id = None
    mgmt_address = None
    ro_community_id = None
    rw_community_id = None

    def __init__(self, host):
        fields = ('id', 'mgmt_address', 'ro_community_id', 'rw_community_id')
        for f in fields:
            setattr(self, f, getattr(host, f))

    @property
    def ro_community(self):
        """ Return the read only community """
        comm = model.SnmpCommunity.by_id(self.ro_community_id)
        if comm is not None:
            DBSession.expunge(comm)
        return comm

    @property
    def rw_community(self):
        """ Return the read write community """
        return model.SnmpCommunity.by_id(self.rw_community_id)


class CacheAttribute(object):
    """ A small shadow of the real Attribute that is not connected to
    the database
    """
    __copy_attrs__ = (
        'id', 'host_id', 'attribute_type_id',
        'index', 'display_name',
        )
    poller_set = None
    poller_row = None

    def __init__(self, attribute):
        for copy_attr in self.__copy_attrs__:
            setattr(self, copy_attr, getattr(attribute, copy_attr))
        self.poller_pos = 0
        self.host = CacheHost(attribute.host)
        self.in_poller = False
        self.skip_rows = []
        self.poller_values = {}
        self.poller_times = {}
        self.start_time = 0

        # Load in the fields AttributeTypeField.tag: AttributeField:value
        self.fields = {af.attribute_type_field.tag: af.value
                       for af in attribute.fields}

    def get_field(self, tag=None, id=None):
        """ Get value of field for this attribute with tag='tag'. """
        try:
            return self.fields[tag]
        except KeyError:
            return None

    def start_polling(self):
        self.start_time = time.time()
        self.in_poller = True

    def stop_polling(self, pos, value):
        self.poller_values[pos] = value
        self.poller_times[pos] = (time.time() - self.start_time)*1000

    def start_backend(self):
        self.start_time = time.time()

    def stop_backend(self):
        self.backend_time = (time.time() - self.start_time)*1000

    def save_value(self, value):
        self.poller_values[self.poller_pos] = value

    def update_poll_time(self):
        attribute = Attribute.by_id(self.id)
        if attribute is not None:
            attribute.update_poll_time()

    def get_poller_row(self):
        if self.poller_set is None:
            return None
        try:
            return self.poller_set[self.poller_pos]
        except IndexError:
            return None
