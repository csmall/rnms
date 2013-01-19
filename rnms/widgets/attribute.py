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
from tw2.jqplugins import jqgrid
from rnms.model import Attribute

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


