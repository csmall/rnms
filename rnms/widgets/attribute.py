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
from tg import url, flash

from sqlalchemy import and_, asc, func

from tw2.jqplugins import jqgrid
from tw2.jqplugins.jqplot import JQPlotWidget
from tw2.jqplugins.jqplot.base import pieRenderer_js
import tw2.core as twc

from rnms.model import Attribute, DBSession
from rnms.lib import states

class AttributeMap(twc.Widget):
    id = 'attribute-map'
    template = 'rnms.templates.widgets.map'
    host_id = None

    def __init__(self):
        self.url = url
        super(AttributeMap, self).__init__()

    def attribute_state(self, attribute):
        """ Returns the attribute state which is used for seveity class
        and description box. Returns
        (class,textual)
        """
        if attribute.admin_state == states.STATE_DOWN:
            return ('asd','Admin Down')
        else:
            alarm = attribute.highest_alarm()
            if alarm is None:
                return ('ok', 'Up')
            else:
                return (str(alarm.event_type.severity_id), alarm.event_type.severity.display_name)
    
    def prepare(self):
        conditions = []
        if self.host_id is not None:
            conditions.append(Attribute.host_id == self.host_id)
        attributes = DBSession.query(Attribute).filter(and_(*conditions)).order_by(asc(Attribute.host_id))
        host_groups = {}
        if attributes.count() == 0:
            flash('No Attributes Found','alert')
            self.map_groups = None
        else:
            for attribute in attributes:
                astate,state_desc = self.attribute_state(attribute)
                
                try:
                    atype = attribute.attribute_type.display_name
                except AttributeError:
                    atype = 'Unknown'
                new_att = (attribute.display_name, astate, attribute.host.display_name, atype, state_desc, ''.join(['<b>{}: </b>{}<br>'.format(k,v) for k,v in attribute.description_dict().items() if v != '']), url('/attributes',{'a':str(attribute.id)}))
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


class AttributeStatusPie(JQPlotWidget):
    """
    Pie Chart of the Attributes' Status """
    id = 'attribute-status-pie'
    resources = JQPlotWidget.resources + [
            pieRenderer_js,
            ]

    options = {
            'seriesColors': [ "#468847", "#F89406", "#B94A48", "#999999", "#3887AD", "#222222"], 
            'seriesDefaults' : {
                'renderer': twc.js_symbol('$.jqplot.PieRenderer'),
                },
            'legend': {
                'show': True,
                'location': 'e',
                },
            }

    def __init__(self, state_data=None, **kwargs):
        super(AttributeStatusPie, self).__init__(**kwargs)
        self.state_list = (states.STATE_UP, states.STATE_ALERT, states.STATE_ADMIN_DOWN, states.STATE_TESTING, states.STATE_UNKNOWN)
        self.state_data = state_data
                
    def prepare(self):
        series = []
        if self.state_data is not None:
            for state in self.state_list:
                try:
                    series.append((states.STATE_NAME[state].capitalize(), self.state_data[state]))
                except KeyError:
                    series.append((states.STATE_NAME[state].capitalize(),0))
        self.data = [ series ]
        super(AttributeStatusPie, self).prepare()



