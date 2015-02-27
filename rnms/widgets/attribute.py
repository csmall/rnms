# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2015 Craig Small <csmall@enc.com.au>
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

from tw2.jqplugins.jqgrid import jqGridWidget
import tw2.core as twc

from rnms.model import Attribute, DBSession, Host, EventState, Event
from rnms.lib import states, structures
from rnms.lib.table import jqGridTableBase

from rnms.widgets.base import MapWidget
from status_pie import StatusPie


class AttributeStatusPie(StatusPie):
    id = 'attribute-status-pie'

    def prepare(self):
        self.state_data = {}
        down_attributes = DBSession.query(Attribute).\
            filter(Attribute.admin_state == states.STATE_DOWN)
        self.state_data[states.STATE_ADMIN_DOWN] = down_attributes.count()

        attributes = DBSession.query(
            func.count(Attribute.admin_state), Attribute.admin_state).\
            group_by(Attribute.admin_state)
        for attribute in attributes:
            self.state_data[attribute[1]] = attribute[0]
        super(AttributeStatusPie, self).prepare()


class AttributeMap(MapWidget):
    id = 'attribute-map'
    host_id = None
    alarmed_only = False

    def attribute_state(self, attribute):
        """ Returns the attribute state which is used for seveity class
        and description box. Returns
        (class,textual)
        """
        if attribute.admin_state == states.STATE_DOWN:
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
            conditions.append(EventState.internal_state != states.STATE_UP)
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


class MiniAttributeGrid(structures.attribute_mini, jqGridTableBase):
    __entity__ = Attribute
    __grid_id__ = 'mini-attributes-grid'
    __url__ = '/attributes/minigriddata'
    __hide_primary_field__ = True
    __omit_fields__ = ('__actions__',)
    __caption__ = 'Attributes'
    __height__ = 190
    __scroll__ = True


class AttributeGrid(structures.attribute, jqGridTableBase):
    __grid_id__ = 'attributes-grid'
    __url__ = '/attributes/griddata'
    __omit_fields__ = ('__actions__',)
    __caption__ = 'Attributes'


class AttributeSelector(jqGridWidget):
    id = 'attribute-selector'
    host_id = None
    options = {
        'datatype': 'json',
        'autowidth':    True,
        'imgpath':      'scripts/jqGrid/themes/green/images',
        'url':          '/attributes/gridselector',
        'caption':      'Attributes',
        'colNames': ('ID', 'Host', 'Attribute',),
        'colModel': [
            {
                'name': 'id', 'id': 'id', 'hidden': True,
            }, {
                'name': 'host',
                'id': 'host',
                'width': 100,
            }, {
                'name': 'attribute',
                'id': 'attribute',
                'width': 100,
            }],
        'multiselect': True,
    }


class DiscoveredAttsGrid(jqGridWidget):
    id = 'discovered-atts-grid'
    host_id = None
    options = {
        'datatype':     'json',
        'autowidth':    True,
        'imgpath':      'scripts/jqGrid/themes/green/images',
        'url':          '/hosts/griddiscover',
        'caption':      'Discovered Attributes',
        'colNames': ('ID', 'Actions', 'Type', 'Index', 'Name',
                     'State', 'Description'),
        'colModel': [
            {
                'name': 'id', 'id': 'id', 'hidden': True,
            }, {
                'name': '__actions__', 'align': 'center', 'width': 30,
            }, {
                'name': 'attribute_type',
                'id': 'attribute_type',
            }, {
                'name': 'index',
                'id': 'index',
                'width': 55,
            }, {
                'name': 'display_name',
                'id': 'display_name',
                'width': 100,
            }, {
                'name': 'state',
                'id': 'state',
                'width': 30,
            }, {
                'name': 'description',
                'id': 'description',
                'width': 100,
            },
        ],
        'viewrecords': True,
        'grouping': True,
        'groupingView': {
            'groupText': ['<b>{0}</b>'],
            'groupField': ['attribute_type', ],
            'groupOrder': ['asc'],
            'groupColumnShow': False,
        },
        'multiselect': True,

    }

    def iprepare(self):
        self.options['url'] += '?h={}'.format(self.host_id)
        super(DiscoveredAttsGrid, self).prepare()


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
                hostid_filter + [Attribute.admin_state == states.STATE_DOWN]
            ))).first()
        self.att_total = int(admin_down[0])
        db_states = DBSession.query(
            EventState.internal_state, func.count(Attribute.id)).\
            join(Attribute).filter(and_(
                *(hostid_filter +
                  [Attribute.admin_state != states.STATE_DOWN]))).\
            group_by(EventState.internal_state)
        tmp_states = {}
        for att in db_states:
            tmp_states[att[0]] = att[1]
            self.att_total += att[1]

        self.att_states = []
        for state_val, label in states.STATE_NAMES.items():
            if state_val is None:
                self.att_states.append((label, admin_down[0]))
            else:
                try:
                    self.att_states.append((label, tmp_states[state_val]))
                except KeyError:
                    self.att_states.append((label, 0))
        super(AttributeSummary, self).prepare()


class AttributeStatusBar(AttributeSummary):
    """ Small full-sized row that shows the status of the attributes in
    one line """

    id = 'attribute-statusbar'
    template = 'rnms.templates.widgets.attribute_statusbar'
