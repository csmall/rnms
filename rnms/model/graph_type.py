# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2011-2013 Craig Small <csmall@enc.com.au>
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
import logging

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, SmallInteger, String

from rnms.model import DeclarativeBase, DBSession
from rnms.lib.parsers import fill_fields

logger = logging.getLogger('rnms')

graph_colors = ("4bb2c5", "c5b47f", "EAA228", "579575", "839557",
                "958c12", "953579", "4b5de4", "d8b83f", "ff5800",
                "0085cc")
class GraphTypeError(Exception): pass
class GraphTypeLineError(Exception): pass

def format_def(rrd_def, attribute):
    """
    Return the DEF: line for this rrd graph definition
    Format is
    <dir>/<rrd_filename>:data:<attribute_type.rra_cf>
    """
    rrd_filename = rrd_def.attribute_type_rrd.filename(attribute.id)
    if rrd_filename is None:
        logger.warning('RRD filename not found')
        return None
    return str(''.join((
            'DEF:',
            rrd_def.name,
            '=',
            rrd_filename,
            ':data:',
            attribute.attribute_type.rra_cf)))

def escape_legend(legend, attribute=None):
    """
    Returns colon escaped legend
    If attribute suppled, replace fields with attribute fields
    """
    if attribute is None:
        return str(legend.replace(':',r'\:'))
    else:
        return str(fill_fields(legend, attribute=attribute).replace(':',r'\:'))

def maxavglast(vname):
    return (
        'VDEF:{0}_max={0},MAXIMUM'.format(vname),
        'VDEF:{0}_avg={0},AVERAGE'.format(vname),
        'VDEF:{0}_last={0},LAST'.format(vname),
    )

def print_line(attribute, line_type, vname, color, legend, legend_unit, 
              stack=False):
    """ Return a list of lines for this specific item """
    esc_units = escape_legend(legend_unit, attribute)
    return (
        '{}:{}#{}:{}{}'.format(line_type, vname, color,
                             escape_legend(legend+': ', attribute),
                               ('',':STACK')[stack]),
        r'GPRINT:{}_max:Max {}'.format(vname, esc_units),
        r'GPRINT:{}_avg:Average {}'.format(vname, esc_units),
        r'GPRINT:{}_last:Last {}\l'.format(vname, esc_units),
    )

class GraphType(DeclarativeBase):
    """
    Main definition of a graph.
    """
    __tablename__ = 'graph_types'

    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    display_name = Column(Unicode(40), nullable=False)
    attribute_type_id = Column(Integer, ForeignKey('attribute_types.id'))
    title = Column(String(40), nullable=False, default='')
    left_label = Column(String(40), nullable=False, default='')
    template = Column(String(20), nullable=False, default='custom')
    extra_options = Column(String(200), nullable=False, default='')
    rrd_lines = relationship('GraphTypeRRDLine', backref='graph_type', cascade='all, delete, delete-orphan')
    defs = relationship('GraphTypeDef', backref='graph_type', cascade='all, delete, delete-orphan')
    vnames = relationship('GraphTypeVname', order_by='GraphTypeVname.position', backref='graph_type', cascade='all, delete, delete-orphan')
    lines = relationship('GraphTypeLine', order_by='GraphTypeLine.position', backref='graph_type', cascade='all, delete, delete-orphan')

    allowed_options = ('lower-limit', 'upper-limit', 'rigid', 'logarithmic', 'base', 'right-axis', 'right-axis-label')

    @classmethod
    def by_id(cls, gt_id):
        """ Return the GraphType with given id"""
        return DBSession.query(cls).filter( cls.id == gt_id).first()

    @classmethod
    def by_display_name(cls, display_name):
        """ Return the GraphType with name"""
        return DBSession.query(cls).filter( cls.display_name == display_name).first()

    def __repr__(self):
        return '<GraphType {}>'.format(self.display_name)

    def vname_by_name(self, name):
        """
        Return the vname from this GraphType that matches the name
        """
        for vname in self.defs:
            if vname.name == name:
                return vname
        for vname in self.vnames:
            if vname.name == name:
                return vname
        return None

    def format(self, attribute):
        """
        Return a tuple of rrdgraph lines based upon the definition of
        this GraphType and the RRDValues of the given attribute
        """
        if self.template == 'custom':
            graph_defs = [ d.format(attribute) for d in self.defs ]
            graph_vnames = [ vname.format(attribute) for vname in self.vnames ]
            graph_lines = [ l.format(attribute) for l in self.lines ]
            return graph_defs + graph_vnames + graph_lines
        try:
            real_format = getattr(self, '_format_'+self.template)
        except AttributeError:
            raise GraphTypeError('No format method for {}'.format(self.template))
        return real_format(attribute)

    def graph_options(self, attribute, start_time=0, end_time=0):
        """
        Return the graph_options for this graph
        """
        graph_options = [
                '--pango-markup',
                #'--legend-position=east',
                '-n', 'TITLE:12:Arial',
                '-n', 'AXIS:7:Arial',
                '-n', 'UNIT:9:Arial',
                '-n', 'LEGEND:9:Arial',
                '-c', 'BACK#ffff8800',
                '-c', 'SHADEA#ffffff00',
                '-c', 'SHADEB#ffffff00',
                '--width', '570',
                '--height', '175',
                '--full-size-mode',
                #'-t', str(attribute.host.display_name + ' - ' + attribute.display_name),
                ]
        for extra_option in self.extra_options.split(' '):
            if extra_option == 'rigid':
                graph_options.append('--rigid')
            else:
                try:
                    opt_name,opt_val = extra_option.split('=')
                except ValueError:
                    pass
                else:
                    if opt_name in self.allowed_options:
                        graph_options.extend(('--'+str(opt_name), str(opt_val)))

        if start_time > 0:
            graph_options.extend(('-s', str(start_time)))

        if end_time > 0:
            graph_options.extend(('-e', str(end_time)))

        if self.left_label != '':
            graph_options.extend(('-v', str(fill_fields(self.vertical_label,attribute=attribute))))

        return graph_options

    def title(self, attribute):
        """ Textual title for this graph and attribute """
        return '{} {} - {}'.format(
            attribute.host.display_name,
            attribute.display_name,
            self.display_name)

    def _format_area(self, attribute):
        """ Format the RRDgraph items for an AREA graph """
        graph_defs = []
        graph_vnames = []
        graph_lines = []
        for idx,line in enumerate(self.rrd_lines):
            color = graph_colors[idx % len(graph_colors)]
            graph_defs.append(line.format_def(attribute))
            line_vname, line_name = line.format_vnames(attribute)
            if line_vname is not None:
                graph_vnames.append(line_vname)
            graph_vnames.extend(maxavglast(line_name))
            graph_lines.extend(
                print_line(attribute, 'AREA', line_name, color,
                           line.legend, line.legend_unit)
                )
        return graph_defs + graph_vnames + graph_lines
    
    def _format_totalarea(self, attribute):
        """ Graph Type for used/free type graphs. First line is a read
        area with the second being green.
        """
        graph_defs = []
        graph_vnames = []
        graph_lines = []
        for idx,line in enumerate(self.rrd_lines):
            graph_defs.append(line.format_def(attribute))
            line_vname, line_name = line.format_vnames(attribute)
            if line_vname is not None:
                graph_vnames.append(line_vname)
            graph_vnames.extend(maxavglast(line_name))
            if idx == 0 :
                graph_lines.extend(
                    print_line(attribute, 'AREA', line_name, 'ff0000',
                               line.legend, line.legend_unit)
                )
            elif idx == 1:
                graph_lines.extend(
                    print_line(attribute, 'AREA', line_name, '00ff00',
                               line.legend, line.legend_unit,True)
                )
        return graph_defs + graph_vnames + graph_lines
    
    def _format_stackedarea(self, attribute):
        """ Graph Type for stacking areas on top of each other 
        """
        graph_defs = []
        graph_vnames = []
        graph_lines = []
        for idx,line in enumerate(self.rrd_lines):
            graph_defs.append(line.format_def(attribute))
            line_vname, line_name = line.format_vnames(attribute)
            if line_vname is not None:
                graph_vnames.append(line_vname)
            graph_vnames.extend(maxavglast(line_name))
            color = graph_colors[idx % len(graph_colors)]
            if idx == 0 :
                graph_lines.extend(
                    print_line(attribute, 'AREA', line_name, color,
                               line.legend, line.legend_unit)
                )
            else:
                graph_lines.extend(
                    print_line(attribute, 'AREA', line_name, color,
                               line.legend, line.legend_unit,True)
                )
        return graph_defs + graph_vnames + graph_lines
    
    def _format_inout(self, attribute):
        """ Format the RRDgraph items for an AREA graph """
        graph_defs = []
        graph_vnames = []
        graph_lines = []
        for idx,line in enumerate(self.rrd_lines):
            if idx == 0:
                template = 'AREA'
                color = '00ff00'
            elif idx == 1:
                template = 'LINE2'
                color = '0000ff'
            else:
                template = 'LINE2'
                color = graph_colors[idx % len(graph_colors)]
            graph_defs.append(line.format_def(attribute))
            line_vname, line_name = line.format_vnames(attribute)
            if line_vname is not None:
                graph_vnames.append(line_vname)
            graph_vnames.extend(maxavglast(line_name))
            graph_lines.extend(
                print_line(attribute, template, line_name, color,
                           line.legend, line.legend_unit)
                )
        return graph_defs + graph_vnames + graph_lines

    def _format_lines(self, attribute):
        """ A Lines format has several lines in a graph """
        graph_defs = []
        graph_vnames = []
        graph_lines = []
        for idx,line in enumerate(self.rrd_lines):
            template = 'LINE2'
            color = graph_colors[idx % len(graph_colors)]
            graph_defs.append(line.format_def(attribute))
            line_vname, line_name = line.format_vnames(attribute)
            if line_vname is not None:
                graph_vnames.append(line_vname)
            graph_vnames.extend(maxavglast(line_name))
            graph_lines.extend(
                print_line(attribute, template, line_name, color,
                           line.legend, line.legend_unit)
                )
        return graph_defs + graph_vnames + graph_lines


class GraphTypeDef(DeclarativeBase):
    """
    Graph Type DEF items - which RRD values are used by this graph
    """
    __tablename__ = 'graph_type_defs'
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    graph_type_id = Column(Integer, ForeignKey('graph_types.id'), nullable=False, default=0)
    name = Column(String(60), nullable=False, default='')
    attribute_type_rrd_id = Column(Integer, ForeignKey('attribute_type_rrds.id'), nullable=False)
    attribute_type_rrd = relationship('AttributeTypeRRD')
    #}

    def __init__(self, graph_type, name, attribute_type_rrd):
        self.graph_type = graph_type
        self.name = name
        self.attribute_type_rrd = attribute_type_rrd

    def format(self, attribute):
        """
        Return the DEF: line for this rrd graph definition """
        return format_def(self, attribute)


class GraphTypeVname(DeclarativeBase):
    """
    Graph Variable Names
    Each GraphType has one or more variable names which are the [CV]DEF
    lines. See rrdgraph_data for more information.
    """
    __tablename__ = 'graph_type_vnames'
    __valid_def_types = ('CDEF', 'VDEF')
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    graph_type_id = Column(Integer, ForeignKey('graph_types.id'), nullable=False, default=0)
    position = Column(SmallInteger, nullable=False,default=0)
    def_type = Column(SmallInteger, nullable=False, default=0) #0,1 CDEF,VDEF
    name = Column(String(60), nullable=False, default='')
    expression = Column(String(250))
    #}

    def __repr__(self):
        return '<GraphTypeVname {}:{}>'.format(self.def_type_name,self.name)

    @property
    def def_type_name(self):
        if not 0 <= self.def_type <= 1:
            raise GraphTypeError('Invalid def_type')
        else:
            return self.__valid_def_types[self.def_type]

    def set_def_type(self, def_type):
        """ Set the def type using a string """
        try:
            self.def_type = self.__valid_def_types.index(def_type)
        except ValueError:
            raise GraphTypeError('Bad def type {} specified'.format(def_type))

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

    def format(self, attribute):
        """
        Print the formatted DEF entry for use in rrdgraphs. If the
        data is not valid return none
        CDEF:name=expression
        VDEF:name=expression
        """
        #print fill_fields(self.expression, attribute=attribute)
        if self.name == '' or self.expression == '' or not 0 <= self.def_type <= len(self.__valid_def_types):
            return None
        return '{}:{}={}'.format(self.def_type_name, self.name, fill_fields(self.expression, attribute=attribute))

    def is_cdef(self):
        """ Return True if this object is a CDEF """
        return self.def_type == 0

    def is_vdef(self):
        """ Return True if this object is a CDEF """
        return self.def_type == 1


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
    graph_type_def_id = Column(Integer, ForeignKey('graph_type_defs.id'))
    graph_type_def = relationship('GraphTypeDef')
    value = Column(String(40))
    legend = Column(String(250), nullable=False, default='')
    color = Column(String(8))

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

    def _set_vname(self, vname):
        """
        The vname could be either a VDEF or CDEF or a DEF. The first two
        go into one column while the third goes in another.
        This method handles that!
        """
        if type(vname) == GraphTypeVname:
            self.vname = vname
        elif type(vname) == GraphTypeDef:
            self.graph_type_def = vname
        else:
            raise ValueError('Unknown vdef type')
    
    def _get_vname(self):
        if not self.vname is None:
            return self.vname
        else:
            return self.graph_type_def

    def set_print(self, vname, fmt):
        """
        Define this Line as a PRINT line using the given vname object
        and the format. vname must be a VDEF
        Output is: PRINT:vname.name:legend
        """
        if not vname.is_vdef():
            raise GraphTypeLineError('vname must be a VDEF')

        self.set_line_type('PRINT')
        self._set_vname(vname)
        self.legend = fmt

    def set_gprint(self, vname, fmt):
        """
        Define this Line as a GPRINT line using the given vname object
        and the format. vname must be a VDEF
        Output is GPRINT:vname.name:legend
        """
        if not vname.is_vdef():
            raise GraphTypeLineError('vname must be a VDEF')

        self.set_line_type('GPRINT')
        self._set_vname(vname)
        self.legend = fmt

    def set_comment(self, comment):
        """
        Define this Line as a COMMENT using the given comment string
        colons are escaped by this method.
        Output is COMMENT:legend
        """
        self.set_line_type('COMMENT')
        self.legend = comment

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
            self._set_vname(vname)
        else:
            if value is None:
                raise GraphTypeLineError('Either vname or value must be defined')
            try:
                float(value)
            except ValueError:
                raise GraphTypeLineError('Vrule time must be a float or integer')
            self.value = value
        self.set_line_type('VRULE')
        self.set_color(color)
        self.legend = legend


    def set_hrule(self, value, color, legend=None):
        """
        Define this Line as a HRULE which is a horizontal line
        at the given value.
        Value must be able to be converted into a float but can be
        a number or an attribute field
        Output is HRULE:legend#color[:legend]
        """
        self.set_line_type('HRULE')
        self.value = value
        self.set_color(color)
        self.legend = legend


    def set_line(self, vname, color=None, width=2, legend=None, stack=False):
        """
        Define this Line as a LINE with the given parameters.
        vname can be any valid type
        Output is LINEwidth:vname.name[#color][:[legend][:STACK]]
        """
        try:
            float(width)
        except ValueError:
            raise GraphTypeLineError('Line width must be a float')

        self.set_line_type('LINE')
        self._set_vname(vname)
        if color is not None:
            self.set_color(color)
        else:
            if legend is not None:
                raise GraphTypeLineError('legend cannot be specified with no color')
        self.legend = legend
        if stack:
            self.value = '{}:1'.format(width)
        else:
            self.value = '{}:0'.format(width)
    
    def set_area(self, vname, color=None, legend=None, stack=False):
        """
        Define this Line as a AREA with the given parameters.
        vname can be any valid type
        Output is AREA:vname.name[#color][:[legend][:STACK]]
        """
        self.set_line_type('AREA')
        self._set_vname(vname)
        if color is not None:
            self.set_color(color)
        elif legend is not None:
            raise GraphTypeLineError('AREA cannot have legend without color')
        self.legend = legend
        if stack:
            self.value = '1'
        else:
            self.value = '0'
    
    def set_tick(self, vname, color, fraction=None, legend=None):
        """
        Define this Line as a TICK with the given vname
        The color can have an alpha
        """
        self.set_line_type('TICK')
        self._set_vname(vname)
        self.set_color(color, True)
        if fraction is not None:
            try:
                float_fraction = float(fraction)
            except ValueError:
                raise GraphTypeLineError('TICK fraction must be a float')
            else:
                if float_fraction > 100.0:
                    raise GraphTypeLineError('TICK fraction cannot be over 100')
            self.value = fraction
        elif legend is not None:
            raise GraphTypeLineError('TICK cannot have legend without fraction')
        self.legend = legend


    def format(self, attribute):
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
        return real_format(attribute)

    def get_legend(self, attribute=None):
        if self.legend is not None:
            return ':' + escape_legend(self.legend, attribute)
        else:
            return ''

    def get_color(self):
        if self.color is None:
            return ''
        return '#'+self.color

    def get_legend_stack(self, do_stack, attribute=None):
        if self.legend is not None:
            if do_stack:
                return self.get_legend(attribute) + ':STACK'
            else:
                return self.get_legend(attribute)
        elif do_stack:
            return '::STACK'
        else:
            return ''


    # Format methods for returing the output
    def format_print(self, attribute):
        return 'GPRINT:{}:{}'.format(
            self._get_vname().name,
            escape_legend(self.legend, attribute))

    def format_gprint(self, attribute):
        return 'GPRINT:{}:{}'.format(
            self._get_vname().name,
            escape_legend(self.legend, attribute))

    def format_comment(self, attribute):
        return 'COMMENT:'+escape_legend(self.legend, attribute)

    def format_vrule(self, attribute):
        if self._get_vname():
            return 'VRULE:{}#{}{}'.format(self._get_vname().name, self.color, self.get_legend(attribute))
        else:
            return 'VRULE:{}#{}{}'.format(self.value, self.color, self.get_legend(attribute))

    def format_hrule(self, attribute):
        try:
            return 'HRULE:{}#{}{}'.format(float(self.value), self.color, self.get_legend(attribute))
        except ValueError:
            value = attribute.get_field(self.value)
            if value is None:
                logger.warning('Bad HRULE field %s', self.value)
                return ''
            try:
                return 'HRULE:{}#{}{}'.format(float(value), self.color, self.get_legend(attribute))
            except ValueError:
                pass
        return ''

    def format_line(self, attribute):
        width,do_stack = self.value.split(':')
        return 'LINE{}:{}{}{}'.format(width,self._get_vname().name, self.get_color(), self.get_legend_stack(do_stack=='1', attribute))

    def format_area(self, attribute):
        return 'AREA:{}{}{}'.format(self._get_vname().name, self.get_color(), self.get_legend_stack(self.value == '1', attribute))


    def format_tick(self, attribute):
        if self.value is not None and self.value != '':
            fraction = ':'+str(self.value)
        else:
            fraction = ''
        return 'TICK:{}#{}{}{}'.format(self._get_vname().name, self.color, fraction, self.get_legend())


class GraphTypeRRDLine(DeclarativeBase):
    __tablename__ = 'graph_type_rrd_lines'
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    graph_type_id = Column(Integer, ForeignKey('graph_types.id'))
    position = Column(SmallInteger, nullable=False,default=0)
    attribute_type_rrd_id = Column(Integer,
                    ForeignKey('attribute_type_rrds.id'), nullable=False)
    attribute_type_rrd = relationship('AttributeTypeRRD')
    multiplier = Column(String(20), nullable=False, default=1)
    legend = Column(String(40), nullable=False, default='')
    legend_unit = Column(String(40), nullable=False, default='')

    @property
    def name(self):
        return self.attribute_type_rrd.name

    def format_def(self, attribute):
        """ Return the DEF lines for this model """
        return format_def(self, attribute)

    def format_vnames(self, attribute):
        if self.multiplier == '':
            return None,self.attribute_type_rrd.name
        else:
            line_name = self.attribute_type_rrd.name+'_mul'
            return ('CDEF:{}={},{}'.format(line_name,
                                           self.attribute_type_rrd.name,
                                           fill_fields(self.multiplier,attribute=attribute)),
                    line_name)
