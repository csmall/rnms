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
#
""" Resources for widgets etc """
import tw2.core as twc
from tg import url

""" JavaScript Resources """
chart_min_js = twc.JSLink(link=url('/javascript/chart.min.js'))
bootstrap_table_js = twc.JSLink(link=url('/javascript/bootstrap-table.min.js'))

""" CSS Resources """
bootstrap_table_css = twc.CSSLink(link=url('/css/bootstrap-table.min.css'))
