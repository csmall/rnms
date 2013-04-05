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

def poll_buffer(poller_buffer, parsed_params, pobj, attribute, poller_row, **kw):
    """
    A poller to yank items out of the poller_buffer
    The parameters define which key is used from the poller_buffer
    """
    ret_fields = []
    if parsed_params == '':
        print 'no params'
        return False
    field_names =  parsed_params.split(',')
    for field_name in field_names:
        try:
            ret_fields.append(poller_buffer[field_name])
        except KeyError:
            ret_fields.append(None)
    pobj.poller_callback(attribute.id, poller_row, ret_fields)
    return True


