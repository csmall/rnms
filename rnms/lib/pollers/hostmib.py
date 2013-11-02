# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
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
# This poller based upon hostmib poller in JFFNMS by Javier Szyszlican
# and Anders Karlsson <anders.x.karlsson@songnetworks.se>


def poll_hostmib_apps(poller_buffer, parsed_params, **kw):
    oid = (1, 3, 6, 1, 2, 1, 25, 4, 2, 1, 2)
    kw['pobj'].snmp_engine.get_table(
        kw['attribute'].host, (oid,), cb_hostmib_apps,
        with_oid=1, **kw)
    return True


def cb_hostmib_apps(values, error, pobj, attribute, **kw):
    if values is None:
        pobj.poller_callback(attribute.id, None)
        return
    app_count = 0
    pids = []
    for ((pid, app),) in values:
        if app == str(attribute.display_name):
            app_count += 1
            pids.append(int(pid))
    state = 'not_running'
    if app_count > 0:
        state = 'running'
    pobj.poller_callback(attribute.id, (state, app_count, pids))


def poll_hostmib_perf(poller_buffer, parsed_params, **kw):
    """
    Find the memory used for this process
    """
    base_oid = (1, 3, 6, 1, 2, 1, 25, 5, 1, 1, 2)
    try:
        if poller_buffer['pids'] != []:
            oids = [base_oid+(pid,) for pid in poller_buffer['pids']]
            return kw['pobj'].snmp_engine.get_list(
                kw['attribute'].host, oids, cb_hostmib_perf,
                default=0, **kw)
    except KeyError:
        pass
    kw['pobj'].poller_callback(kw['attribute'].id, 0)
    return True


def cb_hostmib_perf(values, error, pobj, attribute, **kw):
    total_memory = 0
    if values is not None:
        for pid_mem in values:
            if pid_mem is not None:
                total_memory += int(pid_mem)

    pobj.poller_callback(attribute.id, total_memory)
