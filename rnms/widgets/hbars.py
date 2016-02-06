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
from sqlalchemy import and_, func
import tw2.core as twc
from rnms.model import DBSession, Attribute, EventState
from rnms.lib.states import State


class HBarGraph(twc.Widget):
    """
    Small Horizontal Bar Graph Chart
    graph_data should be a list of 3 item list
    (label, percent, value label)
     """
    template = 'rnms.templates.widgets.hbargraph'
    title = twc.Param('Title of the Chart', default='')
    graph_data = twc.Param('List of (label,pct,val)')


class HBarAttributeStatus(HBarGraph):
    """
    Horizontal Bar Chart showing the attribute status counts
    """
    host_id = twc.Param("Only Show Attributes for given Host ID", default=None)

    def prepare(self):
        hostid_filter = []
        attribute_count = 0
        if self.host_id is not None:
            hostid_filter = [Attribute.host_id == self.host_id]
        admin_down = DBSession.query(func.count(Attribute.id)).\
            filter(and_(*(
                hostid_filter + [Attribute.admin_state == State.DOWN]
            ))).first()
        attribute_count += int(admin_down[0])

        db_states = DBSession.query(
            EventState.internal_state, func.count(Attribute.id)).\
            join(Attribute).filter(and_(
                *(hostid_filter +
                  [Attribute.admin_state != State.DOWN]))).\
            group_by(EventState.internal_state)
        tmp_states = {}
        for att in db_states:
            tmp_states[att[0]] = att[1]
            attribute_count += att[1]

        self.graph_data = []
        for state_val, label in State.NAMES.items():
            if state_val == State.ADMIN_DOWN:
                self.graph_data.append((
                    label.capitalize(),
                    admin_down[0]*100/attribute_count,
                    admin_down[0]))
            else:
                try:
                    self.graph_data.append(
                        (label.capitalize(),
                         tmp_states[state_val]*100/attribute_count,
                         tmp_states[state_val]))
                except KeyError:
                    self.graph_data.append((label.capitalize(), 0, 0))
        super(HBarGraph, self).prepare()
