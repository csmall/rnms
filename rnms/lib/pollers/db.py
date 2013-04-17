# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012 Craig Small <csmall@enc.com.au>
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
def poll_db(poller_buffer, **kwargs):
    """
    Retrive an item for this attribute
    """
    cb_db(kwargs['poller_row'].poller.parameter, None, kwargs)
    return True

def cb_db(value, error, kwargs):
    """
    CallBack function for a simple poller. This should kick off
    the return functions in the PollerRow
    """
    kwargs['pobj'].poller_callback(kwargs['attribute'], value)

        
