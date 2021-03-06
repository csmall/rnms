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
from tg import url, flash

from sqlalchemy import and_, asc, func

import tw2.core as twc

from rnms.model import Attribute, DBSession, Host, EventState, Event
from rnms.lib.states import State
from rnms.lib.resources import pnotify_core_js

from rnms.widgets.base import MapWidget
from .bootstrap_table import BootstrapTable

__all__ = ['AttributeMap', 'AttributeDetails', 'AttributeDiscoverTable']


class AttributeMap(MapWidget):
    id = 'attribute-map'
    host_id = None
    alarmed_only = False

    def attribute_state(self, attribute):
        """ Returns the attribute state which is used for seveity class
        and description box. Returns
        (class,textual)
        """
        if attribute.admin_state == State.DOWN:
            return ('asd', 'Admin Down')
        else:
            alarm = Event.attribute_alarm(attribute.id)
            if alarm is None:
                return ('ok', 'Up')
            else:
                return (alarm.event_state.severity_id,
                        alarm.event_state.display_name.capitalize())

    def prepare(self):
        conditions = []
        if self.host_id is not None:
            conditions.append(Attribute.host_id == self.host_id)
        if self.alarmed_only:
            conditions.append(EventState.internal_state != State.UP)
        attributes = DBSession.query(Attribute).join(Host, EventState).\
            filter(and_(*conditions)).\
            order_by(asc(Host.display_name), asc(Attribute.display_name))
        if attributes.count() == 0:
            flash('No Attributes Found', 'alert')
            self.map_groups = None
        else:
            for attribute in attributes:
                astate, state_desc = self.attribute_state(attribute)

                try:
                    atype = attribute.attribute_type.display_name
                except AttributeError:
                    atype = 'Unknown'
                att_fields = [('Host', attribute.host.display_name),
                              ('Type', atype),
                              ('Status', state_desc), ]
                for k, v in attribute.description_dict().items():
                    if v != '':
                        att_fields.append((k, v))
                self.add_item(attribute.host_id, attribute.host.display_name,
                              [('Address', attribute.host.mgmt_address)],
                              {'name': attribute.display_name,
                               'state': astate,
                               'url': url('/attributes/'+str(attribute.id)),
                               'fields': att_fields,
                               })
        super(AttributeMap, self).prepare()


class AttributeSummary(twc.Widget):

    id = 'attribute-summary'
    template = 'rnms.templates.widgets.attribute_summary'

    def prepare(self):
        self.url = url
        hostid_filter = []
        if hasattr(self, 'host_id') and self.host_id is not None:
            hostid_filter = [Attribute.host_id == self.host_id]

        admin_down = DBSession.query(func.count(Attribute.id)).\
            filter(and_(*(
                hostid_filter + [Attribute.admin_state == State.DOWN]
            ))).first()
        self.att_total = int(admin_down[0])
        db_states = DBSession.query(
            EventState.internal_state, func.count(Attribute.id)).\
            join(Attribute).filter(and_(
                *(hostid_filter +
                  [Attribute.admin_state != State.DOWN]))).\
            group_by(EventState.internal_state)
        tmp_states = {}
        for att in db_states:
            tmp_states[att[0]] = att[1]
            self.att_total += att[1]

        self.att_states = []
        for state_val, label in State.NAMES.items():
            if state_val is None:
                self.att_states.append((label, admin_down[0]))
            else:
                try:
                    self.att_states.append((label, tmp_states[state_val]))
                except KeyError:
                    self.att_states.append((label, 0))
        super(AttributeSummary, self).prepare()


class AttributeDetails(twc.Widget):
    """
    Widget to present the details of the given Attribute
    """
    template = 'rnms.templates.widgets.attribute_details'
    attribute = twc.Param('The attribute record out of the DB query')
    extra = twc.Param('Additional data outside the DB query', default=None)


class AttributeDiscoverTable(BootstrapTable):
    id = 'discover_table'
    host_id = twc.Param('ID# of Host to discover')
    have_checkbox = True
    hidden_columns = ['id', 'fields', ]
    columns = [('action', 'Action'),
               ('display_name', 'Name'),
               ('attribute_type', 'Attribute Type'),
               ('admin_state', 'Admin State'),
               ('oper_state', 'Oper State'),
               ]

    def prepare(self):
        self.resources.append(pnotify_core_js)
        self.data_url = url('/attributes/discoverdata.json',
                            {'h': self.host_id})
