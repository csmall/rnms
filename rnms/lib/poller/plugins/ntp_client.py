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


def ntp_reply(pobj, attribute_id, is_synch, info):
    if is_synch is True:
        sync = u'synchronized'
    else:
        sync = u'unsynchronized'
    pobj.poller_callback(attribute_id, {'state': sync, 'info': info})


def poll_ntp_client(poller_buffer, **kwargs):
    """
    A poller for checking if a NTP server is synchronised.
    We consider a server to be synchronised if there is one of the peers
    is a system peer
    Returns True on success, False on error
    """
    return kwargs['pobj'].ntp_client.get_peers(kwargs['attribute'].host,
                                               cb_ntp_peer_list, **kwargs)


def cb_ntp_peer_list(values, error, host, **kw):
    """
    First callback with the list of peers """
    for a_id, a_selection in values:
        if a_selection == 6:  # system peer found
            kw['pobj'].ntp_client.get_peer_by_id(host, a_id,
                                                 cb_peer_details, **kw)
            return
    ntp_reply(kw['pobj'], kw['attribute'].id, False, 'no peer list returned')


def cb_peer_details(response_packet, error, host, pobj, attribute, **kw):
    if response_packet.assoc_data == {}:
        ntp_reply(pobj, attribute.id, False, 'no details returned')
        return
    # find the source address
    try:
        srcadr = response_packet.assoc_data['srcadr']
    except KeyError:
        ntp_reply(pobj, attribute.id, False, 'peer srcadr not found')
    else:
        ntp_reply(pobj, attribute.id, True, 'with {0}'.format(srcadr))
