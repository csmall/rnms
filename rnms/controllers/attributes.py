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
#
"""Attribute controller module"""
import datetime
from sqlalchemy import select,func

# turbogears imports
from tg import expose, request
#from tg import redirect, validate, flash

# third party imports
import tw2.sqla
#from tg.i18n import ugettext as _
#from repoze.what import predicates

# project specific imports
from rnms.lib.base import BaseController
#from rnms.model import DBSession, metadata, Event, EventSeverity,EventType, DeclarativeBase
#from rnms.widgets import AttributeGrid, RRDWidget, AttributeGrid2
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

    @expose('json')
    def jqsumdata(self, page=1, rows=1, *args, **kw):
        rows = int(rows)
        page = int(page)
        start_row = page * rows
        end_row = (page+1) * rows

        attributes =model.DBSession.query(model.Attribute)
        row_count = attributes.count()
        data=[]
        for attribute in attributes[start_row:end_row]:
            data.append({
                'cell' : [ attribute.display_name,
                attribute.oper_state_name(),
                attribute.admin_state_name(),
                ],
                'id': attribute.id})
        return dict(page=page,records=row_count,total=row_count/rows, rows=data)
#    @expose('json')
    #def jqgrid(self, *args, **kwargs):
    #    return AttributeGrid2.request(request).body

    #@expose('rnms.templates.attribute.graph')
    #def graph(self, graphid):
    #    rrdwidget = RRDWidget()
    #    rrdwidget.rrd_filenames = [
    #            '/var/local/jffnms-website/rrd/interface-2731-0.rrd'
    #            ]
    #    rrdwidget.start = (datetime.datetime.today() - datetime.timedelta(1))
    #    return dict(page="graph", rrdwidget=rrdwidget)

