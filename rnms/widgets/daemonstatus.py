# -*- coding: utf-8 -*-
#
# This file is part of the RoseNMS
#
# Copyright (C) 2016 Craig Small <csmall@enc.com.au>
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
import tw2.core as twc
import zmq
from rnms.lib import zmqmessage

__all__ = ['DaemonStatus']


class DaemonStatus(twc.Widget):
    template = 'rnms.templates.widgets.daemonstatus'
    threads = []

    def prepare(self):
        context = zmq.Context()
        socket = zmqmessage.info_client(context)
        thread_info = zmqmessage.get_info(socket)
        socket.close()
        context.destroy()
        if thread_info is not None:
            self.threads.append({'name': 'Main Daemon', 'alive': True})
            self.threads.extend(thread_info['tasks'])
        else:
            self.threads.append({'name': 'Main Daemon', 'alive': False})
        super(DaemonStatus, self).prepare()
