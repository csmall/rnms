# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2013-2014 Craig Small <csmall@enc.com.au>
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
from tg import url
from rnms import model

wanted_stats = (
        ('Alarms', model.Event.alarmed_events([]), 'alarms'),
        ('Zones', model.Zone, 'zones'),
        ('Hosts', model.Host, 'hosts'),
        ('Events', model.Event, 'events'),
        ('Attributes', model.Attribute, 'attributes'),
        )


def get_overall_statistics():
    """ Return a dictionary of statistics """
    return {
            'alarms': model.Event.alarmed_events([]).count(),
            'zones': model.DBSession.query(model.Zone).count(),
            'hosts': model.DBSession.query(model.Host).count(),
            'attributes': model.DBSession.query(model.Attribute).count(),
            }
