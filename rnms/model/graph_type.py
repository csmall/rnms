# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011 Craig Small <csmall@enc.com.au>
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
import re

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, SmallInteger, String

from rnms.model import DeclarativeBase

class GraphTypeError(Exception): pass
class GraphTypeLineError(Exception): pass

class GraphTypeGroup(DeclarativeBase):
    """
    A group of graph types that are available for a particular attribute
    type.  The display name is used to select the graphs for the attribute
    in the GUI. There can be two graphs (left and right) within each
    GraphTypeGroup entry.
    """
    __tablename__ = 'graph_type_groups'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40), nullable=False)
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'), nullable=False )
    attribute_type = relationship('AttributeType', backref='graph_groups')
    left_graph_id = Column(Integer, ForeignKey('graph_types.id'))
    left_graph = relationship('GraphType', primaryjoin="GraphTypeGroup.left_graph_id==GraphType.id")
    right_graph_id = Column(Integer, ForeignKey('graph_types.id'))
    right_graph = relationship('GraphType', primaryjoin="GraphTypeGroup.right_graph_id==GraphType.id")
    #}

class GraphType(DeclarativeBase):
    """
    Main definition of a graph. Referenced by the graph group.
    """
    __tablename__ = 'graph_types'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    vnames = relationship('GraphTypeVname', order_by='GraphTypeVname.position', backref='graph_type', cascade='all, delete, delete-orphan')
    lines = relationship('GraphTypeLine', order_by='GraphTypeLine.position', backref='graph_type', cascade='all, delete, delete-orphan')

class GraphTypeVname(DeclarativeBase):
    """
    Graph Variable Names
    Each GraphType has one or more variable names which are the [CV|]DEF
    lines. See rrdgraph_data for more information.
    """
    __tablename__ = 'graph_type_vnames'
    __valid_def_types = ('DEF', 'CDEF', 'VDEF')
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    graph_type_id = Column(Integer, ForeignKey('graph_types.id'), nullable=False, default=0)
    position = Column(SmallInteger, nullable=False,default=0)
    def_type = Column(SmallInteger, nullable=False, default=0) #0,1,2 DEF,CDEF,VDEF
    name = Column(String(60), nullable=False, default='')
    expression = Column(String(250))
    #}

    def __repr__(self):
        return '<GraphTypeVname {}:{}>'.format(self.def_type_name,self.name)

    @property
    def def_type_name(self):
        if not 0 <= self.def_type <= 2:
            raise GraphTypeError('Invalid def_type')
        else:
            return self.__valid_def_types[self.def_type]

    def set_def_type(self, def_type):
        """ Set the def type using a string """
        try:
            self.def_type = self.__valid_def_types.index(def_type)
        except ValueError:
            raise GraphTypeError('Bad def type {} specified'.format(def_type))

    def set_def(self, name, expression):
        """ Create this object as a DEF """
        self.set_def_type('DEF')
        self.name = name
        self.expression = expression

    def set_cdef(self, name, expression):
        """ Create this object as a CDEF """
        self.set_def_type('CDEF')
        self.name = name
        self.expression = expression

    def set_vdef(self, name, expression):
        """ Create this object as a VDEF """
        self.set_def_type('VDEF')
        self.name = name
        self.expression = expression

    def format(self):
        """
        Print the formatted DEF entry for use in rrdgraphs. If the
        data is not valid return none
        DEF:name=name of attribute's RRD
        CDEF:name=expression
        VDEF:name=expression
        """
        if self.name == '' or self.expression == '' or not 0 <= self.def_type <= len(self.__valid_def_types):
            return None
        return '{}:{}={}'.format(self.def_type_name, self.name, self.expression)

    def is_def(self):
        """ Return True if this object is a DEF """
        return self.def_type == 0
    
    def is_cdef(self):
        """ Return True if this object is a CDEF """
        return self.def_type == 1

    def is_vdef(self):
        """ Return True if this object is a CDEF """
        return self.def_type == 2


class GraphTypeLine(DeclarativeBase):
    """
    All GraphTypes must have one or more GraphTypeLine objects defined. These
    are the graph elements that either draw lines, areas etc or print
    comments.  See man page rrdgraph_graph for more details.
    """
    __tablename__ = 'graph_type_lines'
    __valid_line_types = ('PRINT', 'GPRINT', 'COMMENT', 'VRULE', 'HRULE', 'LINE', 'AREA', 'TICK', 'SHIFT')
    color_re = re.compile(r'^[0-9a-f]{6}$', re.I)
    color_alpha_re = re.compile(r'^[0-9a-f]{6}(?:[0-9a-f]{2})?$', re.I)
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    graph_type_id = Column(Integer, ForeignKey('graph_types.id'))
    position = Column(SmallInteger, nullable=False,default=0)
    line_type = Column(Integer, nullable=False, default=0) #LINE1,AREA<PRINT
    vname_id = Column(Integer, ForeignKey('graph_type_vnames.id'))
    vname = relationship('GraphTypeVname')
    expression = Column(String(250), nullable=False, default='')
    color = Column(String(8))
    legend= Column(Unicode(40))

    #}
    def __repr__(self):
        return '<GraphTypeLine type={}>'.format(self.line_type_name)

    @classmethod
    def line_type_by_name(self, name):
        try:
            return self.__valid_line_types.index(name)
        except ValueError:
            return None

    @property
    def line_type_name(self):
        return self.__valid_line_types[self.line_type]

    def set_line_type(self, line_type):
        """ Set the line type using a string """
        try:
            self.line_type = self.__valid_line_types.index(line_type)
        except ValueError:
            raise GraphTypeLineError('Bad line type {} specified'.format(line_type))

    def set_color(self, color, has_alpha=False):
        """
        Sets the objects color by first checking that it is in a valid 
        format. May optionally have an alpha layer
        """
        if has_alpha:
            if self.color_alpha_re.match(color) is None:
                raise GraphTypeLineError('Color should be 6 or 8 hex characters')
        else:
            if self.color_re.match(color) is None:
                raise GraphTypeLineError('Color should be 6 hex characters')
        self.color = color

    def set_print(self, vname, fmt):
        """
        Define this Line as a PRINT line using the given vname object
        and the format. vname must be a VDEF
        Output is: PRINT:vname.name:expression
        """
        if not vname.is_vdef():
            raise GraphTypeLineError('vname must be a VDEF')

        self.set_line_type('PRINT')
        self.vname = vname
        self.expression = fmt

    def set_gprint(self, vname, fmt):
        """
        Define this Line as a GPRINT line using the given vname object
        and the format. vname must be a VDEF
        Output is GPRINT:vname.name:expression
        """
        if not vname.is_vdef():
            raise GraphTypeLineError('vname must be a VDEF')

        self.set_line_type('GPRINT')
        self.vname = vname
        self.expression = fmt

    def set_comment(self, comment):
        """
        Define this Line as a COMMENT using the given comment string
        colons are escaped by this method.
        Output is COMMENT:expression
        """
        self.set_line_type('COMMENT')
        self.expression = comment

    def set_vrule(self, vname, value, color, legend=None):
        """
        Define this line as a VRULE which is a verical line
        at a specific time.  Either the vname or value 
        (but not both) must be defined and a vname must be a VDEF
        value must be unix epoch
        Output is
          VRULE:value#color[:legend]
          VRULE:vname.name#color[:legend]
        """
        if vname is not None:
            if not vname.is_vdef():
                raise GraphTypeLineError('vrule vname must be a VDEF')
            if value is not None:
                raise GraphTypeLineError('vrule requires ONE of value or vname only')
            self.vname = vname
        else:
            if value is None:
                raise GraphTypeLineError('Either vname or value must be defined')
            try:
                fvalue = float(value)
            except ValueError:
                raise GraphTypeLineError('Vrule time must be a float or integer')
            self.expression = value
        self.set_line_type('VRULE')
        self.set_color(color)
        self.legend = legend


    def set_hrule(self, value, color, legend=None):
        """
        Define this Line as a HRULE which is a horizontal line
        at the given value.
        Value must be able to be converted into a float
        Output is HRULE:expression#color[:legend]
        """
        try:
            dummy = float(value)
        except ValueError:
            raise GraphTypeLineError('value must be a float')

        self.set_line_type('HRULE')
        self.expression = value
        self.set_color(color)
        self.legend = legend


    def set_line(self, vname, color=None, width=2, legend=None, stack=False):
        """
        Define this Line as a LINE with the given parameters.
        vname can be any valid type
        Output is LINEwidth:vname.name[#color][:[legend][:STACK]]
        """
        try:
            dummy = float(width)
        except ValueError:
            raise GraphTypeLineError('Line width must be a float')

        self.set_line_type('LINE')
        self.vname = vname
        if color is not None:
            self.set_color(color)
        else:
            if legend is not None:
                raise GraphTypeLineError('legend cannot be specified with no color')
        self.legend = legend
        if stack:
            self.expression = '{}:1'.format(width)
        else:
            self.expression = '{}:0'.format(width)
    
    def set_area(self, vname, color=None, legend=None, stack=False):
        """
        Define this Line as a AREA with the given parameters.
        vname can be any valid type
        Output is AREA:vname.name[#color][:[legend][:STACK]]
        """
        self.set_line_type('AREA')
        self.vname = vname
        if color is not None:
            self.set_color(color)
        elif legend is not None:
            raise GraphTypeLineError('AREA cannot have legend without color')
        self.legend = legend
        if stack:
            self.expression = '1'
        else:
            self.expression = '0'
    
    def set_tick(self, vname, color, fraction=None, legend=None):
        """
        Define this Line as a TICK with the given vname
        The color can have an alpha
        """
        self.set_line_type('TICK')
        self.vname = vname
        self.set_color(color, True)
        if fraction is not None:
            try:
                float_fraction = float(fraction)
            except ValueError:
                raise GraphTypeLineError('TICK fraction must be a float')
            else:
                if float_fraction > 100.0:
                    raise GraphTypeLineError('TICK fraction cannot be over 100')
            self.expression = fraction
        elif legend is not None:
            raise GraphTypeLineError('TICK cannot have legend without fraction')
        self.legend = legend


    def format(self):
        """
        Print the formatted line entry for use in rrdgraph
        """
        line_type_name = self.line_type_name
        if line_type_name is None:
            raise GraphTypeLineError('No line type for format')
        try:
            real_format = getattr(self, 'format_'+line_type_name.lower())
        except AttributeError:
            raise GraphTypeLineError('No format method for {}'.format(line_type_name))
        return real_format()

    def get_legend(self):
        if self.legend is not None:
            return ':"'+self.legend.replace(':', r'\:')+'"'
        else:
            return ''

    def get_color(self):
        if self.color is None:
            return ''
        return '#'+self.color

    def get_legend_stack(self, do_stack):
        if self.legend is not None:
            if do_stack:
                return '{}:STACK'.format(self.get_legend())
            else:
                return self.get_legend()
        elif do_stack:
            return '::STACK'
        else:
            return ''

    def escape_expression(self):
        """ Returns colon escaped expression """
        return self.expression.replace(':',r'\:')

    # Format methods for returing the output
    def format_print(self):
        return 'PRINT:{}:{}'.format(self.vname.name, self.escape_expression())

    def format_gprint(self):
        return 'GPRINT:{}:{}'.format(self.vname.name, self.escape_expression())

    def format_comment(self):
        return 'COMMENT:{}'.format(self.escape_expression())

    def format_vrule(self):
        if self.vname:
            return 'VRULE:{}#{}{}'.format(self.vname.name, self.color, self.get_legend())
        else:
            return 'VRULE:{}#{}{}'.format(self.expression, self.color, self.get_legend())

    def format_hrule(self):
        return 'HRULE:{}#{}{}'.format(self.expression, self.color, self.get_legend())

    def format_line(self):
        width,do_stack = self.expression.split(':')
        return 'LINE{}:{}{}{}'.format(width,self.vname.name, self.get_color(), self.get_legend_stack(do_stack=='1'))

    def format_area(self):
        return 'AREA:{}{}{}'.format(self.vname.name, self.get_color(), self.get_legend_stack(self.expression == '1'))


    def format_tick(self):
        if self.expression is not None and self.expression != '':
            fraction = ':'+str(self.expression)
        else:
            fraction = ''
        return 'TICK:{}#{}{}{}'.format(self.vname.name, self.color, fraction, self.get_legend())


