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

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, SmallInteger, String

from rnms.model import DeclarativeBase


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

class GraphTypeVname(DeclarativeBase):
    """
    Graph Variable Names
    Each GraphType has one or more variable names which are the [CV|]DEF
    lines. See rrdgraph_data for more information.
    """
    __tablename__ = 'graph_type_vnames'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    graph_type_id = Column(Integer, ForeignKey('graph_types.id'), nullable=False)
    position = Column(SmallInteger, nullable=False,default=0)
    def_type = Column(SmallInteger, nullable=False) #CdEF,VDEF,DATA
    name = Column(String(60), nullable=False)
    expression = Column(String(250), nullable=False)
    #}

class GraphTypeGraph(DeclarativeBase):
    """
    All GraphTypes must have one or more GraphTypeGraph lines defined. These
    are the graph elements that either draw lines, areas etc or print
    comments.  See man page rrdgraph_graph for more details.
    """
    __tablename__ = 'graph_type_graphs'
    
    #{ Columns
    id = Column(Integer, autoincrement=True, primary_key=True)
    position = Column(SmallInteger, nullable=False,default=0)
    command = Column(String(20), nullable=False) #LINE1,AREA<PRINT
    vname_id = Column(Integer, ForeignKey('graph_type_vnames.id'))
    vname = relationship('GraphTypeVname')
    expression = Column(String(250), nullable=False)
    colour = Column(String(6), nullable=False, default='00ff00')
    legend= Column(Unicode(40))

    #}

