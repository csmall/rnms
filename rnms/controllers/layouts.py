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
""" Layout controller
Layouts are a series of portlets
"""

# turbogears imports
from tg import expose
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates

# project specific imports
from rnms.lib.base import BaseController
#from rnms.model import DBSession, metadata


class LayoutsController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    #allow_only = authorize.not_anonymous()
    
    @expose('rnms.templates.layout')
    def index(self):
        import tw2.core as twc
        import tw2.forms as twf
        from tw2.jqplugins import portlets
        class layout(portlets.ColumnLayout):
            width='590px'
            class col1(portlets.Column):
                width='50%'
                class por1(portlets.Portlet):
                    width='100%'
                    title = 'hello'
                    one_widget = twf.Label(text='Some content in a label widget')
            class col2(portlets.Column):
                width='50%'
                class por2(portlets.Portlet):
                    width='100%'
                    title = 'hello2'
                    one_widget = twf.Label(text='Some content in a label widget')
        return dict(page='index',w=layout)
