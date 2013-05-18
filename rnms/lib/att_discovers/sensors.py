# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012-2013 Craig Small <csmall@enc.com.au>
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
""" Discover lm-sensors attributes """

from rnms import model

# reply_row, snmp_table, unit
# snmp_table is third last row of the oids defined below
sensor_types = (
        (0, '2', 'degC', 'Temperature', '0.001'),
        (1, '3', 'RPM', 'Fan Speed', '1'),
        (2, '4', 'V', 'Voltage', '0.001'),
        (3, '5', 'V', 'Voltage', '0.001'),
        )

def discover_sensors(dobj, att_type, host):
    """
    Run snmpwalk on the lm-sensors table
    """
    oids = (
             (1,3,6,1,4,1,2021,13,16,2,1,2), #temperature
             (1,3,6,1,4,1,2021,13,16,3,1,2), # fan
             (1,3,6,1,4,1,2021,13,16,4,1,2), # volt
             (1,3,6,1,4,1,2021,13,16,5,1,2), # misc
             )
    return dobj.snmp_engine.get_table(
        host, oids, cb_sensors, table_trim=1,
        host=host, dobj=dobj, att_type=att_type)

def cb_sensors(values, error, host, dobj, att_type):
    sensors = {}
    last_sensor = ''
    for valkey,table_index,sunit,measure,multiplier in sensor_types:
        keys = sorted([int(x) for x in values[valkey]])
        for key in keys:
            idx = str(key)
            sensor_name = values[valkey][idx]
            # This is a hack, some lmsesnor code shows the same device
            # multiple times (current, min, max, alarm, other)
            # other devices show it once
            # We take the first index
            if sensor_name == last_sensor:
                continue
            new_sensor = model.DiscoveredAttribute(host.id, att_type)
            new_sensor.display_name = sensor_name
            new_sensor.index = '{}.{}'.format(table_index, idx)
            new_sensor.set_field('table_index', table_index)
            new_sensor.set_field('row_index', idx)
            new_sensor.set_field('units', sunit)
            new_sensor.set_field('measure', measure)
            new_sensor.set_field('multiplier', multiplier)
            sensors[new_sensor.index] = new_sensor
            last_sensor = sensor_name

    dobj.discover_callback(host.id, sensors)
