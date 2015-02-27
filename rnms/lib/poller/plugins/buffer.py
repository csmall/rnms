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


def poll_buffer(poller_buffer, parsed_params, pobj, attribute, **kw):
    """
    A poller to yank items out of the poller_buffer
    The parameters define which key is used from the poller_buffer
    """
    ret_fields = []
    if parsed_params == '':
        pobj.logger.error('A:%d - buffer poller requires parameters',
                          attribute.id)
        return False
    ret_fields = [poller_buffer.get(name, None) for name in
                  parsed_params.split(',')]
    pobj.poller_callback(attribute.id, ret_fields)
    return True
