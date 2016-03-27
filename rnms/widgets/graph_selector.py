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
import tw2.core as twc
from tg import url

from rnms.lib.resources import c3_min_js, c3_min_css, d3_min_js

__all__ = ['GraphSelector', ]


class GraphSelector(twc.Widget):
    template = 'rnms.templates.widgets.graph_selector'
    attribute_id = twc.Param('ID# for pre-selected widget', default=None)
    label = 'Graph Type'

    def prepare(self):
        self.resources.append(c3_min_js)
        self.resources.append(d3_min_js)
        self.resources.append(c3_min_css)
        self.aoption_url = url('/attributes/option')
        self.hoption_url = url('/hosts/option')
        self.coption_url = url('/attribute_client_option')
        self.gtoption_url = url('/graphs/types_option')
        self.atoption_url = url('/attributes/type_option')
