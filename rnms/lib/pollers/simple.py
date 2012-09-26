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
def poll_simple(poller, attribute):
    """
    Simple poller that returns what is in the poller attribute
    Good for showing an example
    Returns True on success, False on error
    """
    poll_simple_cb(poller.parameter, attribute.host)
    return True

def poll_simple_cb(value, host, kwargs, error=None):
    """
    CallBack function for a simple poller. This should kick off
    the return functions in the PollerRow
    """
    if error is not None:
        return None
    return value
        
