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


def poll_db(poller_buffer, parsed_params, attribute, pobj, **kwargs):
    """
    Retrieve a value out of the database for this attribute
    It does this using the parsed parameters feature, so if
    you have an attribute with a value of speed, setting the
    parameters to ${speed} will do it
    """
    pobj.poller_callback(attribute.id, parsed_params)
    return True
