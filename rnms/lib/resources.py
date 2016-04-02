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
from tg import lurl

""" JavaScript Resources """
jquery_js = twc.JSLink(link=lurl('/javascript/jquery.min.js'))
chart_min_js = twc.JSLink(link=lurl('/javascript/chart.min.js'))
bootstrap_table_js = twc.JSLink(
    link=lurl('/javascript/bootstrap-table.min.js'))
c3_min_js = twc.JSLink(link=lurl('/javascript/c3.min.js'))
d3_min_js = twc.JSLink(link=lurl('/javascript/d3.min.js'))
pnotify_core_js = twc.JSLink(link=lurl('/javascript/notify/pnotify.core.js'))
pnotify_buttons_js = twc.JSLink(
    link=lurl('/javascript/notify/pnotify.buttons.js'))
pnotify_nonblock_js = twc.JSLink(
    link=lurl('/javascript/notify/pnotify.nonblock.js'))

""" CSS Resources """
bootstrap_table_css = twc.CSSLink(link=lurl('/css/bootstrap-table.min.css'))
c3_min_css = twc.CSSLink(link=lurl('/css/c3.min.css'))
