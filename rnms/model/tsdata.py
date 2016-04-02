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
""" Time Series Data for Attribute Types """
import time

from sqlalchemy import ForeignKey, Column, and_
from sqlalchemy.types import Integer, Unicode, String, SmallInteger, BigInteger

from rnms.model import DeclarativeBase, DBSession, AttributeField,\
    AttributeTypeField
from rnms.lib.tsdbworker import get_influxclient, InfluxDBClientError

__all__ = ['AttributeTypeTSData']


class AttributeTypeTSData(DeclarativeBase):
    """
    Attribute Types have zero to many Time Series Data elements
    attached to the definition. The TSData elements are stored in the
    Time Series Database, such as Influx DB
    """
    __tablename__ = 'attribute_type_tsdatas'
    __data_type_names__ = ['counter', 'gauge']

    data_type = None

    # { Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    attribute_type_id = Column(Integer, ForeignKey("attribute_types.id"),
                               nullable=False)
    display_name = Column(Unicode(40), nullable=False)
    name = Column(String(40))
    position = Column(SmallInteger, nullable=False, default=1)
    range_min = Column(Integer)
    range_max = Column(BigInteger)
    range_max_field = Column(String(40))  # matches tag in fields
    data_type = Column(SmallInteger, nullable=False, default=0)
    # 0:counter, 1:gauge
    # }

    @classmethod
    def by_name(cls, attribute_type_id, name):
        """ Return the RRD for this attribute_type with the given name """
        return DBSession.query(cls).filter(and_(
                cls.attribute_type_id == attribute_type_id,
                cls.name == name)).first()

    def parse_range_max(self, attribute_id):
        """
        range_max can either be the value stored in that field, or
        derived from an attributes field
        """
        if self.range_max_field == '':
            return self.range_max
        attribute_field = DBSession.query(AttributeField).filter(and_(
            AttributeField.attribute_id == attribute_id,
            AttributeField.attribute_type_field_id == AttributeTypeField.id,
            AttributeTypeField.tag == self.range_max_field)).first()
        if attribute_field is None:
            return 'U'
        new_max = int(attribute_field.value)
        if new_max == 0:
            return 'U'
        return new_max

    @classmethod
    def fix_time(self, timestr):
        if timestr[-1] == 'Z':
            timestr = timestr[:-1]
        utctime = time.mktime(
            time.strptime(timestr.split('.')[0], "%Y-%m-%dT%H:%M:%S"))
        mytime = utctime - time.timezone + (time.daylight * 3600)
        return time.strftime(
            '%Y-%m-%d %H:%M',
            time.localtime(mytime))

    def calc_interval(self, start_time, end_time):
        """ Work out the interval start time can either be
        seconds since epoch or a timespan number of seconds"""
        if start_time < 0:
            timespan = -start_time
        else:
            if end_time is None:
                end_time = time.time()
            timespan = end_time - start_time
        if timespan < 43200:  # 1/2 day
            return '5m'
        if timespan < 2419200:  # 4 weeks
            return '1h'
        return '1d'

    def fetch(self, attribute_id, start_time, end_time=None):
        """ Return the values for a chart """
        client = get_influxclient()
        if client is None:
            return

        measurement = 'A{}'.format(attribute_id)
        interval = self.calc_interval(start_time, end_time)
        if self.data_type == 0:
            query_str =\
                'SELECT NON_NEGATIVE_DERIVATIVE(first({0}),{1}) AS {0} '.\
                format(self.name, interval)
            groupby = 'GROUP BY time({})'.format(interval)
        else:
            query_str = 'SELECT first({0}) AS {0} '.format(self.name)
            groupby = 'GROUP BY time({0})'.format(interval)

        query_str += (
            'FROM {} WHERE time > {}s '.
            format(measurement, start_time) +
            groupby)
        try:
            results = client.query(query_str)
        except InfluxDBClientError as err:
            raise InfluxDBClientError(
                'Problem with query: \'{}\' - {}'.format(
                    query_str, err.message))

        times = []
        values = []
        for row in results.get_points():
            times.append(self.fix_time(row['time']))
            values.append(row[self.name])
        return (times, values)

    @property
    def data_type_name(self):
        """ Return the text name of this data type """
        if self.data_type is None:
            return 'None'
        try:
            return self.__data_type_names__[self.data_type]
        except IndexError:
            return 'Unknown: {}'.format(self.data_type)
