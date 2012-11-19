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
# This poller is based upon the JFFNMS poller of the same name
# Copyright (C) <2002-2005> Javier Szyszlican <javier@szysz.com>

# For details on setting ip accounting up see
# http://www.cisco.com/en/US/tech/tk648/tk362/technologies_configuration_example09186a0080094aa2.shtml

import logging

from rnms.lib import snmp

logger = logging.getLogger('pSAagent')

def poll_cisco_saagent(poller_buffer, parsed_params, **kw):
    """
    Obtain data about the Cisco SA Agent.  
    Parameters: <index>|<qtype>
      <index>: The SA Agent index
      <qtype>: query type, must be one of the keys in the table above
    """
    oid = (1,3,6,1,4,1,9,9,42,1,5,2,1)
    saagent_queries = {
        'fwd_jitter' : ((8,9,13,14),  cb_fwd_jitter),
        'bwd_jitter' : ((18,19,23,24), cb_bwd_jitter),
        'packetloss' : ((1,2,26,27), cb_packetloss),
        }

    index, qtype = parsed_params.split('|')
    try:
        (queries, cb_fun) = saagent_queries[qtype]
    except KeyError:
        logger.errror('Bad query type %s', qtype)
        return False

    req = snmp.SNMPRequest(kw['attribute'].host)
    req.set_replyall(True)
    req.oid_trim = 2
    for query in queries:
        req.add_oid(oid + (query,int(index)), cb_fun, data=kw)
    kw['pobj'].snmp_engine.get(req)
    return True

def cb_fwd_jitter(values, error, pobj, attribute, poller_row, **kw):
    index = str(attribute.index)
    try:
        nr = int(values['8.'+index]) + int(values['13.'+index])
        sum_val = int(values['9.'+index]) + int(values['14.'+index])
    except KeyError:
        pobj.poller_callback(attribute.id, poller_row, None)
    else:
        jitter=0
        if nr > 0:
            jitter = sum_val / nr
        pobj.poller_callback(attribute.id, poller_row, jitter)

def cb_bwd_jitter(values, error, pobj, attribute, poller_row, **kw):
    index = str(attribute.index)
    try:
        nr = int(values['18.'+index]) + int(values['23.'+index])
        sum_val = int(values['19.'+index]) + int(values['24.'+index])
    except KeyError:
        pobj.poller_callback(attribute.id, poller_row, None)
    else:
        jitter=0
        if nr > 0:
            jitter = sum_val / nr
        pobj.poller_callback(attribute.id, poller_row, jitter)


def cb_packetloss(values, error, pobj, attribute, poller_row, **kw):
    index = str(attribute.index)
    try:
        nr = int(values['1.'+index])
        rtt_sum = int(values['2.'+index])
        fwd_pl = int(values['26.'+index])
        bwd_pl = int(values['27.'+index])
    except KeyError:
        pobj.poller_callback(attribute.id, poller_row, None)
    else:
        if nr == 0:
            pobj.poller_callback(attribute.id, poller_row, (0,0,0))
            return
        rtt = rtt_sum / nr
        fwd_pl_pct = fwd_pl / (fwd_pl + nr) * 100
        bwd_pl_pct = bwd_pl / (bwd_pl + nr) * 100
        pobj.poller_callback(attribute.id, poller_row, (fwd_pl_pct,bwd_pl_pct,rtt))

