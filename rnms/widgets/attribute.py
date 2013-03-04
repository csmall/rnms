# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012 Craig Small <csmall@enc.com.au>
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
from tg import url

from sqlalchemy import and_, asc, func

from tw2.jqplugins import jqgrid
import tw2.core as twc

from rnms.model import Attribute, DBSession
from rnms.lib import states

class AttributeMap(twc.Widget):
    id = 'attribute-map'
    template = 'rnms.templates.widgets.map'
    host_id = twc.Param('Limit Attributes by this host id')

    def __init__(self):
        self.host_id = None
        self.url = url
        super(AttributeMap, self).__init__()

    def prepare(self):
        conditions = []
        if self.host_id is not None:
            conditions.append(Attribute.host_id == self.host_id)
        attributes = DBSession.query(Attribute).filter(and_(*conditions)).order_by(asc(Attribute.host_id))
        host_groups = {}
        for attribute in attributes:
            if attribute.admin_state == states.STATE_DOWN:
                astate = 'asd'
            else:
                alarm = attribute.highest_alarm()
                if alarm is None:
                    astate = 'ok'
                else:
                    astate = alarm.event_type.severity_id
            new_att = (' '.join((attribute.display_name, attribute.description())), astate)
            try:
                host_groups[attribute.host_id][1].append(new_att)
            except KeyError:
                host_groups[attribute.host_id]=(attribute.host, [new_att,])
        self.map_groups = [hg for hg in host_groups.values()]
        super(AttributeMap,self).prepare()


class AttributeSummary(twc.Widget):

    id = 'attribute-summary'
    template = 'rnms.templates.widgets.attribute_summary'

    host_id = twc.Param('Limit Attributes by this host id')

    def prepare(self):
        hostid_filter=[]
        if self.host_id is not None:
            hostid_filter = [Attribute.host_id == self.host_id]
        
        admin_down = DBSession.query(func.count(Attribute.id)).filter(and_(*(hostid_filter + [Attribute.admin_state == states.STATE_DOWN]))).first()
        self.att_total = int(admin_down[0])
        db_states = DBSession.query(Attribute.oper_state,func.count(Attribute.id)).filter(and_(*(hostid_filter + [Attribute.admin_state != states.STATE_DOWN]))).group_by(Attribute.oper_state)
        tmp_states = {}
        for att in db_states:
            tmp_states[att[0]] = att[1]
            self.att_total += att[1]
        
        self.att_states = []
        for state_val,label in states.STATE_NAMES.items():
            if state_val is None:
                self.att_states.append((label,admin_down[0]))
            else:
                try:
                    self.att_states.append((label,tmp_states[state_val]))
                except KeyError:
                    self.att_states.append((label, 0 ))
        super(AttributeSummary, self).prepare()

class AttributeGrid(jqgrid.jqGridWidget):
    id ='attribute-grid-id'
    options = {
            'pager' : 'attribute-grid-pager',
            'url' : '/attributes/jqsumdata',
            'datatype': 'json',
            'colNames' : ['Type', 'Name', 'Description', 'Oper', 'Admin'],
            'colModel' : [
                {
                    'name' : 'attribute_type',
                    'width': 100,
                } , {
                    'name' : 'display_name',
                    'width': 100,
                } , {
                    'description' : 'description',
                    'width' : 200,
                } , {
                    'name' : 'oper_state',
                    'width': 60,
                },{
                    'name' : 'admin_state',
                    'width': 60,
                },],
            'rowNum': 15,
            'rowList': [15,30,50],
            'viewrecords': True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'height': 'auto',
            }   

    pager_options = { "search" : True, "refresh" : True, "add" : False,
            "edit": False }
     
    def prepare(self, **kw):
        if self.host_id is not None:
            self.options['postData'] = {'hostid': self.host_id}
            pass#self.options['url'] = self.options['url'] + '/' + str(self.host_id)

        super(AttributeGrid, self).prepare()


