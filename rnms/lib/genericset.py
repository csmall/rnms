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
#
"""Objects that have child rows"""

class GenericSet():
    """
    A generic object that has child rows
    row object MUST have a field called position
    """
    rows = []

    def insert(self, new_pos, new_row):
        """ Add a new row to position pos"""
        for row in self.rows:
            if row.position >= new_pos:
                row.position=row.position+1

        new_row.position=new_pos
        self.rows.insert(new_pos,new_row)

    def append(self, new_row):
        """ Add new PollerRow to PollerSet at the bottom of the Set"""
        new_position=0
        for row in self.rows:
            if new_row is not row:
                new_position=row.position+1
        new_row.position=new_position
        self.poller_rows.append(new_row)

    def row_to(self, position, moving_row):
        """
        Move existing row in set to be at new position in Set.
        Renumbers subsequent Row positions down one.
        """
        for row in self.rows:
            if moving_row is not row and row.position >= position:
                row.position=row.position+1
        moving_row.position=position

    def row_swap(self, position_a, position_b):
        """ Swap position of rows that are the specified positions. If the
        positions don't exist then dont do anything
        """
        for row_a in self.poller_rows:
            if row_a.position == position_a:
                for row_b in self.poller_rows:
                    if row_b.position == position_b:
                        row_a.position = position_b
                        row_b.position = position_a
                        return True
        return False


