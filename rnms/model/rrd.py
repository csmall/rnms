# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011,2012 Craig Small <csmall@enc.com.au>
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
""" RRD field for Attribute Types """
import os
import rrdtool

from sqlalchemy import ForeignKey, Column, and_
from sqlalchemy.types import Integer, Unicode, String, SmallInteger
#from sqlalchemy.orm import relation, backref

from rnms.model import DeclarativeBase, DBSession, AttributeField, AttributeTypeField

dst_names = { 0: 'GAUGE', 1: 'COUNTER', 2: 'ABSOLUTE' }

class AttributeTypeRRD(DeclarativeBase):
    """
    AttributeTypes may have RRD fields attached to their definition
    """
    __tablename__ = 'attribute_type_rrds'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    attribute_type_id = Column(Integer, ForeignKey("attribute_types.id"),nullable=False)
    display_name = Column(Unicode(40), nullable=False)
    name = Column(String(40))
    position = Column(SmallInteger,nullable=False,default=1)
    data_source_type = Column(SmallInteger) # gauge,counter,absolute
    range_min = Column(Integer)
    range_max = Column(Integer)
    range_max_field = Column(String(40)) # matches tag in fields
    #}

    @classmethod
    def by_name(cls, attribute_type, name):
        """ Return the RRD for this attribute_type with the given name """
        print "by name {0} and name {1}".format(attribute_type.id, name)
        return DBSession.query(cls).filter(and_(
                cls.attribute_type_id == attribute_type.id,
                cls.name==name)).first()


    def create(self, filename, attribute):
        """
        Create a new RRD file of this RRD field for the given attribute
        Returns RRD object on success, otherwise None
        """
        # def rra, res, step
        # step ?? from attribute_type.???
        # ds-name: seems to be data, maybe rename?
        # DST: self.data_source_type
        #   heartbeat attribute_type.ds_heartbeat
        #   min self.range_min
        #   max self.range_max

        # CF: attribute.type.rra_cf
        #  xff 0.5 
        #  steps 1
        #  rows attribute_type.rra_rows
        ds_defn = "DS:data:{0}:{1}:{2}:{3}".format(self.dst2str(), self.attribute_type.ds_heartbeat, self.range_min, self.parse_range_max(attribute))
        rra_defn = "RRA:{0}:0.5:1:{1}".format(self.attribute_type.rra_cf, self.attribute_type.rra_rows)
        try:
            rrdtool.create(filename, [ds_defn], rra_defn)
        except rrdtool.error as errmsg:
            print "rrdtool error {0} {1} {2}".format(errmsg,ds_defn,rra_defn)
            return False
        try:
            rrdtool.info(filename)
        except rrdtool.error as errmsg:
            #FIXME - logging error
            return False
        return True

    def parse_range_max(self, attribute):
        """
        range_max can either be the value stored in that field, or
        derived from an attributes field
        """
        if self.range_max_field == '':
            return self.range_max
        attribute_field = DBSession.query(AttributeField).filter(and_(
            AttributeField.attribute == attribute,
            AttributeField.attribute_type_field_id == AttributeTypeField.id,
            AttributeTypeField.tag == self.range_max_field)).first()
        if attribute_field is None:
            return 'U'
        new_max = int(attribute_field.value)
        if new_max == 0:
            return 'U'
        return new_max



    def filename(self, attribute):
        """
        Returns the on-disk filename for this RRD and the given attribute
        Returns none if attribute doesn't have this RRD field
        Format is <rrd_dir>/<attribute_id>-<rrd_position>.rrd
        If the file doesn't exist, it is created
        """
        # FIXME = dodgy fixed rrd dir
        rrd_dir = '/var/tmp'
        if self.attribute_type_id != attribute.attribute_type_id:
            return None
        filename=  "{0}{1}{2}-{3}{4}rrd".format(
                rrd_dir, os.sep, attribute.id, 
                self.position, os.extsep)
        if os.path.isfile(filename):
            return filename
        if self.create(filename, attribute):
            return filename
        return None

    def update(self, attribute, value):
        """
        Update the RRD file for the given attribute with the given value
        Returns a key:value on success or error message
        """
        filename = self.filename(attribute)
        if filename is None:
            return '(No filename)'
        try:
            rrdtool.update(filename, "N:{0}".format(value))
        except rrdtool.error as errmsg:
            return '(error {0})'.format(errmsg)
        return value

    def adjust_limits(self, attribute, new_min, new_max):
        """ Adjust the RRD DS maximum and minimum """
        filename = self.filename(attribute)
        if filename is None:
            return False
        try:
            rrdtool.tune(filename, "--minimum", new_min, "--maximum", new_max)
        except rrdtool.error:
            # FIXME logging
            return False
        return True

    def dst2str(self):
        """ Return string representation of DST field"""
        return dst_names.get(self.data_source_type, None)

