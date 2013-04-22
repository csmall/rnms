# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
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
""" Hosts Widgets """
from tw2.jqplugins.jqgrid import jqGridWidget
from tw2.jqplugins.jqgrid.base import word_wrap_css
from tw2 import core as twc


class HostsGrid(jqGridWidget):
    id = 'hosts-grid-id'
    options = {
            'pager': 'hosts-grid-pager',
            'url': '/hosts/griddata',
            'colNames': [ 'Host Name', 'Zone' ],
            'datatype': 'json',
            'colModel' : [
                {
                    'name': 'display_name',
                    'width': 30,
                    'align': 'left',
                },{
                    'name': 'zone_display_name',
                    'width': 30,
                    'align': 'left',
                }],
            'viewrecords': True,
            'imgpath': 'scripts/jqGrid/themes/green/images',
            'width': 900,
            'height': 'auto',
            }
    def prepare(self):
        self.resources.append(word_wrap_css)
        super(HostsGrid, self).prepare()


