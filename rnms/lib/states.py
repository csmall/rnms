# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2016 Craig Small <csmall@enc.com.au>
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
from collections import OrderedDict

__all__ = ['State']


class State(object):
    """
    Used to provide the fixed internal states for various other
    classes including Events, Alarms. Uses the same IDs as the
    SNMP oper and admin states
    """
    UP = 1
    DOWN = 2
    TESTING = 3
    UNKNOWN = 4
    ALERT = 5
    ADMIN_DOWN = 99  # This is strictly not a state but often used

    _STATES = [UP, DOWN, TESTING, UNKNOWN, ALERT, ADMIN_DOWN]

    NAMES = OrderedDict([
        (UP,       'up'),
        (DOWN,     'down'),
        (TESTING,  'testing'),
        (UNKNOWN,  'unknown'),
        (ALERT,    'alert'),
        (ADMIN_DOWN, 'admin down'),
        ])

    """ Colors in RGB triple """
    _COLORS = OrderedDict([
        (UP,         (70,  136,  71)),
        (DOWN,       (185,  74,  72)),
        (TESTING,    (248, 148,   6)),
        (UNKNOWN,    (153, 153, 153)),
        (ALERT,      (56,  135, 173)),
        (ADMIN_DOWN, (34,   34,  34)),
        ])

    _RGB_COLORS = OrderedDict([
        (UP,       '#468847'),
        (DOWN,     '#F89406'),
        (TESTING,  '#B94A48'),
        (UNKNOWN,  '#999999'),
        (ALERT,    '#3887AD'),
        (ADMIN_DOWN, '#222222'),
        ])

    _mystate = None

    def __init__(self, mystate=None, name=None):
        if mystate is not None:
            mystate = int(mystate)
            if mystate not in self._STATES:
                raise ValueError('{} is not a valid state ID'.format(mystate))
            self._mystate = mystate
        elif name is not None:
            for idx, sname in self.NAMES.items():
                if name == sname:
                    self._mystate = idx
                    break
            else:
                raise ValueError('{} is not a valid state name')

    def __int__(self):
        if self._mystate is not None:
            return self._mystate
        return self.UNKNOWN

    @property
    def name(self):
        """ Return the state name for the given value, if known """
        return self.NAMES[self._mystate]

    @classmethod
    def hex_colors(cls):
        """ Return a list of RGB hex colors """
        return ['#{:02x}{:02x}{:02x}'.format(*cls._COLORS[s])
                for s in cls._STATES]

    def hex_color(self):
        """ Return the RGB hex color string for the state """
        return '#{:02x}{:02x}{:02x}'.format(*self._COLORS[self._mystate])

    def rgb_color(self):
        """ Return the RGB triple color for the state """
        return self._COLORS[self._mystate]

    def rgb_color_str(self):
        """ Return the RGB color triple for the state as a string """
        return ', '.join(map(str, self._COLORS[self._mystate]))
