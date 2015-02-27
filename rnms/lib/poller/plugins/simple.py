# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2012-2013 Craig Small <csmall@enc.com.au>
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


def poll_simple(poller_buffer, parsed_params, **kwargs):
    """
    Simple poller that returns what is in the poller attribute
    Good for showing an example
    Returns True on success, False on error
    """
    cb_simple(parsed_params, None, kwargs)
    return True


def cb_simple(value, error, kwargs):
    """
    CallBack function for a simple poller. This should kick off
    the return functions in the PollerRow
    """
    kwargs['pobj'].poller_callback(kwargs['attribute'], value)

        
