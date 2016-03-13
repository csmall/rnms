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

from sqlalchemy import ForeignKey, Column, and_
from sqlalchemy.types import Integer, Unicode, String, SmallInteger, BigInteger

from rnms.model import DeclarativeBase, DBSession, AttributeField, AttributeTypeField

__all__ = ['AttributeTypeTSData']


class AttributeTypeTSData(DeclarativeBase):
    """
    Attribute Types have zero to many Time Series Data elements
    attached to the definition. The TSData elements are stored in the
    Time Series Database, such as Influx DB
    """
    __tablename__ = 'attribute_type_tsdatas'

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
