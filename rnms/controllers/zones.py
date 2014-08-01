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
""" Zone controller """

# turbogears imports
from tg import expose
#from tg.decorators import require

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates
#from formencode import validators

# project specific imports
from rnms.lib import structures
from rnms.lib import permissions
from rnms.lib.base import BaseGridController
from rnms.lib.table import jqGridTableFiller
from rnms.model import DBSession, Zone
from rnms.widgets import MainMenu, ZoneGrid


class ZonesController(BaseGridController):

    allow_only = permissions.host_ro

    @expose('rnms.templates.zone_index')
    def index(self):
        zone_grid = ZoneGrid()
        return dict(page='host', main_menu=MainMenu,
                    zone_grid=zone_grid)

    @expose('json')
    def griddata(self, *args, **kw):
        class TableFiller(structures.zone, jqGridTableFiller):
            pass
        return super(ZonesController, self).griddata(
            TableFiller, {}, **kw)

    @expose('rnms.templates.widgets.select')
    def option(self):
        zones = DBSession.query(Zone.id, Zone.display_name).all()
        zones.insert(0, ('', '-- Choose Zone --'))
        return dict(items=zones)
