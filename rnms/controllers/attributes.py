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
#
"""Attribute controller module"""
import datetime
from sqlalchemy import select,func

# turbogears imports
from tg import expose, request
from tg import redirect, validate, flash
from sqlalchemy import and_

# third party imports
import tw2.sqla
#from tg.i18n import ugettext as _
#from repoze.what import predicates
from formencode import validators
from tw2.jqplugins.ui import set_ui_theme_name
from sqlalchemy import asc

# project specific imports
from rnms.lib.base import BaseController
#from rnms.model import DBSession, metadata, Event, EventSeverity,EventType, DeclarativeBase
#from rnms.widgets import AttributeGrid, RRDWidget, AttributeGrid2
from rnms.widgets.attribute import AttributeSummary
from rnms import model

def recursive_update(d1, d2):
      """ Little helper function that does what d1.update(d2) does,
      but works nice and recursively with dicts of dicts of dicts.
   
      It's not necessarily very efficient.
      """
   
      for k in d1.keys():
          if k not in d2:
              continue
   
          if isinstance(d1[k], dict) and isinstance(d2[k], dict):
              d1[k] = recursive_update(d1[k], d2[k])
          else:
              d1[k] = d2[k]
   
      for k in d2.keys():
          if k not in d1:
              d1[k] = d2[k]
   
      return d1

class AttributesController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()
    
    #@expose('rnms.templates.widget')
    #def index(self, *args, **kw):
    #    return dict(widget=AttributeGrid2, page='attribute')
    @expose('rnms.templates.widgets.map')
    def map(self):
        attributes = model.DBSession.query(model.Attribute).order_by(asc(model.Attribute.host_id))
        host_groups = {}
        for attribute in attributes:
            alarm = attribute.highest_alarm()
            if alarm is None:
                astate = 0
            else:
                astate = alarm.event_type.severity_id
            new_att = ('{} {}'.format(attribute.display_name, attribute.description()), astate)
            try:
                host_groups[attribute.host_id]['attributes'].append(new_att)
            except KeyError:
                host_groups[attribute.host_id] = {'display_name': attribute.host.display_name, 'attributes': [new_att,]}

        return dict(att_groups = ([(hg['display_name'], hg['attributes']) for hg in host_groups.values()]
            ))

    @expose('json')
    @validate(validators={'hostid':validators.Int()})
    def jqsumdata(self, hostid=0, page=1, rows=1, *args, **kw):
        rows = int(rows)
        page = int(page)
        start_row = page * rows
        end_row = (page+1) * rows

        conditions = []
        if hostid > 0:
            conditions.append(model.Attribute.host_id == hostid)
        attributes =model.DBSession.query(model.Attribute).filter(and_(*conditions))
        row_count = attributes.count()
        data=[]
        for attribute in attributes[start_row:end_row]:
            data.append({
                'cell' : [ attribute.attribute_type.display_name,
                    attribute.display_name,
                attribute.description(),
                attribute.oper_state_name(),
                attribute.admin_state_name(),
                ],
                'id': attribute.id})
        return dict(page=page,records=row_count,total=row_count/rows, rows=data)
#    @expose('json')
    #def jqgrid(self, *args, **kwargs):
    #    return AttributeGrid2.request(request).body

    @expose('rnms.templates.widget')
    def att_summary(self):
        w= AttributeSummary()
        return dict(widget=w)
    #@expose('rnms.templates.attribute.graph')
    #def graph(self, graphid):
    #    rrdwidget = RRDWidget()
    #    rrdwidget.rrd_filenames = [
    #            '/var/local/jffnms-website/rrd/interface-2731-0.rrd'
    #            ]
    #    rrdwidget.start = (datetime.datetime.today() - datetime.timedelta(1))
    #    return dict(page="graph", rrdwidget=rrdwidget)

