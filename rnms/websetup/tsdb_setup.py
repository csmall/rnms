# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2016 Craig Small <csmall@enc.com.au>
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
from tg import config

from influxdb import InfluxDBClient


def tsdb_setup():
    """ Setup the Influx Database """
    try:
        influx_dsn = config['influx_dsn']
    except KeyError:
        print('Configuration is missing key: influx_dsn')
        exit()

    influx_client = InfluxDBClient.from_DSN(influx_dsn)
    print ('Connected to Influx DB using URL {0._baseurl}'.
           format(influx_client))
    influx_client.create_database(influx_client._database)
    print ("Created Influx database \"{0._database}\"".
           format(influx_client))
