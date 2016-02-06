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
""" Events Widgets """
from tg import url

from bootstrap_table import BootstrapTable

__all__ = ['EventTable']


class EventTable(BootstrapTable):
    template = 'rnms.templates.widgets.eventtable'
    data_url = url('/events/tabledata.json')
    enable_search = True
    columns = [('created', 'Date'),
               ('severity', 'Severity'),
               ('host', 'Host'),
               ('attribute', 'Attribute'),
               ('event_type', 'Type'),
               ('description', 'Description')]
    detail_url = url('/events/')
    row_formatter = {'severity': 'formatSeverity'}
    sort_column = 'created'
    sort_asc = False
    striped = True
