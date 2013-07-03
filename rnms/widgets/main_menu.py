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

""" Main menu """
from tw2 import core as twc
from tw2.jquery import jquery_js
import tg

from rnms.lib import permissions

class MainMenu(twc.Widget):
    id = 'main-menu'
    template = 'rnms.templates.widgets.main_menu'
    resources = twc.Widget.resources + [jquery_js]
    page = None

    def __init__(self, **kw):
        self.page = kw['page']
        return super(MainMenu, self).__init__(**kw)

    def prepare(self):
        self.tg = tg
        self.permissions={
            'manage': tg.predicates.has_permission('manage'),
            'host': permissions.host_ro,
        }
        self.logged_in = tg.request.identity
