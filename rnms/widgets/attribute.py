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
from sqlalchemy import func
from sqlalchemy import and_

from tw2.jqplugins import jqgrid
import tw2.core as twc

from rnms.model import Attribute, DBSession
from rnms.lib.states import *

class AttributeSummary(twc.Widget):
    state_names = (('Up', STATE_UP), ('Alert', STATE_ALERT), ('Down', STATE_DOWN), ('Admin Down', None), ('Unknown', STATE_UNKNOWN))

    id = 'attribute-summary'
    template = 'rnms.templates.widgets.attribute_summary'

    host_id = twc.Param('Limit Attributes by this host id')

    def prepare(self):
        hostid_filter=[]
        if self.host_id is not None:
            hostid_filter = [Attribute.host_id == self.host_id]
        
        admin_down = DBSession.query(func.count(Attribute.id)).filter(and_(*(hostid_filter + [Attribute.admin_state == STATE_DOWN]))).first()
        self.att_total = int(admin_down[0])
        db_states = DBSession.query(Attribute.oper_state,func.count(Attribute.id)).filter(and_(*(hostid_filter + [Attribute.admin_state != STATE_DOWN]))).group_by(Attribute.oper_state)
        tmp_states = {}
        for att in db_states:
            tmp_states[att[0]] = att[1]
            self.att_total += att[1]
        
        self.att_states = []
        for label,state_val in self.state_names:
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


