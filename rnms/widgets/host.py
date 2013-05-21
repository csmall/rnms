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
from tg import flash, url
from sqlalchemy import and_, asc
from tw2.jqplugins.jqgrid import jqGridWidget
from tw2.jqplugins.jqgrid.base import word_wrap_css

from base import MapWidget
from rnms.model import DBSession, Host, Zone, Event

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


class HostMap(MapWidget):
    id = 'host-map'
    zone_id = None
    alarmed_only = False

    def __init__(self):
        self.url = url
        super(HostMap, self).__init__()

    def host_state(self, host):
        """ Returns the host state which is used for severity class and
        description box. Returns (class,text)
        """
        alarm = Event.host_alarm(host.id)
        if alarm is None:
            return ('ok', 'Up')
        else:
            return (alarm.event_type.severity_id, alarm.alarm_state.display_name.capitalize())

    def prepare(self):
        conditions = []
        conditions.append(Host.show_host == True)
        if self.zone_id is not None:
            conditions.append(Host.zone_id == self.zone_id)
        hosts = DBSession.query(Host).join(Zone).filter(and_(*conditions)).\
                order_by(asc(Zone.display_name), asc(Host.display_name))
        if hosts.count() == 0:
            flash('No Hosts Found',  'alert')
            self.map_groups = None
        else:
            for host in hosts:
                vendor,device = host.snmp_type()
                hstate,state_desc = self.host_state(host)
                if self.alarmed_only == True and hstate == 'ok':
                    continue
                host_fields = [ ('Zone', host.zone.display_name),
                              ('Status', state_desc),
                              ('Vendor', vendor),
                              ('Device', device),
                              ('Address', host.mgmt_address),]
                self.add_item(host.zone_id, host.zone.display_name,
                              [],
                              {'name': host.display_name,
                               'state': hstate,
                               'url': url('/attributes/map/',{'h': host.id}),
                               'fields': host_fields,
                              })
        super(HostMap, self).prepare()

