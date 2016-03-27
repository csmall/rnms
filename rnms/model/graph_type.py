# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2011-2016 Craig Small <csmall@enc.com.au>
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
""" Main description of a type of graph """
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, SmallInteger, String

from rnms.model import DeclarativeBase, DBSession
from rnms.lib.parsers import fill_fields

SI_UNITS = (
    ('T', 1e12),
    ('G', 1e9),
    ('M', 1e6),
    ('k', 1e3),
    ('', 1),
    ('m', 0.001))


class GraphTypeError(Exception):
    pass


class GraphTypeLineError(Exception):
    pass


class GraphType(DeclarativeBase):
    """
    Main definition of a graph.
    """
    __tablename__ = 'graph_types'

    # { Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40), nullable=False)
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    title = Column(String(40), nullable=False, default='')
    left_label = Column(String(40), nullable=False, default='')
    template = Column(String(20), nullable=False, default='custom')
    extra_options = Column(String(200), nullable=False, default='')
    lines = relationship('GraphTypeLine', backref='graph_type',
                         cascade='all, delete, delete-orphan')
    allowed_options = ('lower-limit', 'upper-limit', 'rigid', 'logarithmic',
                       'base', 'right-axis', 'right-axis-label')

    @classmethod
    def by_id(cls, gt_id):
        """ Return the GraphType with given id"""
        return DBSession.query(cls).filter(cls.id == gt_id).first()

    @classmethod
    def by_display_name(cls, display_name):
        """ Return the GraphType with name"""
        return DBSession.query(cls).filter(cls.display_name == display_name).\
            first()

    def __repr__(self):
        return '<GraphType {}>'.format(self.display_name)

    def formatted_title(self, attribute):
        """ Return the Graph Type title using variables from the given
        Attribute"""
        if self.title:
            return fill_fields(self.title, attribute=attribute)
        return self.display_name

    def line_colors(self):
        """ Return the series of line colors """
        return {'data1': '#0000ff', 'data2': '#00ff00'}


class GraphTypeLine(DeclarativeBase):
    __tablename__ = 'graph_type_lines'
    # { Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    graph_type_id = Column(Integer, ForeignKey('graph_types.id'))
    position = Column(SmallInteger, nullable=False, default=0)
    attribute_type_tsdata_id = Column(
        Integer,
        ForeignKey('attribute_type_tsdatas.id'), nullable=False)
    attribute_type_tsdata = relationship('AttributeTypeTSData')
    multiplier = Column(String(20), nullable=False, default='')
    legend = Column(String(40), nullable=False, default='')
    legend_unit = Column(String(40), nullable=False, default='')

    @property
    def name(self):
        return self.attribute_type_tsdata.name

    def formatted_legend(self, attribute):
        return fill_fields(self.legend, attribute=attribute)

    def format_value(self, value, attribute):
        """ Return a formatted string of the given value """
        if value is None:
            return ''
        if self.legend_unit == '':
            return str(value)
        fmt = self.legend_unit
        mult_pos = fmt.find('%s')
        if mult_pos > -1:
            si_unit, divisor = self.get_si_unit(value)
            fmt = fmt.replace('%s', si_unit)
            value = value/float(divisor)
        else:
            mult_pos = fmt.find('%S')
            if mult_pos > -1:
                si_unit, divisor = self.get_si_unit(value)
                fmt = fmt.replace('%S', si_unit)
                value = value/float(divisor)
        # If we are showing as percent, update the value
        pct_pos = fmt.find('%%')
        if pct_pos > -1:
            value *= 100
        fmt = fill_fields(fmt, attribute=attribute)
        return fmt % value

    def get_si_unit(self, value):
        """ Return unit,divisor tuple for SI unit eg 2000 = k,1000 """
        if value == '0':
            return '', 1
        for unit, divisor in SI_UNITS:
            if value >= divisor:
                return unit, divisor
        return unit, divisor
