# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012,2013 Craig Small <csmall@enc.com.au>
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
""" Discover Alteon Real Servers, Virtal Servers and Real Services """

from rnms import model

def discover_alteon_realservers(dobj, att_type, host):
    oids = (
            (1,3,6,1,4,1,1872,2,1,5,2,1,1),
            (1,3,6,1,4,1,1872,2,1,5,2,1,2),
            (1,3,6,1,4,1,1872,2,1,5,2,1,4),
            (1,3,6,1,4,1,1872,2,1,5,2,1,10),
            (1,3,6,1,4,1,1872,2,1,5,2,1,12),
            (1,3,6,1,4,1,1872,2,1,9,2,2,1,7),
            )
    return dobj.snmp_engine.get_many(
        host, oids, cb_alteon_realservers, with_oid=1,
        dobj=dobj, att_type=att_type)


def cb_alteon_realservers(values, error, host, dobj, att_type):
    rservers = {}
    if values is not None:
        for idx in values[0].values():
            try:
                ipaddress = values[1][idx]
            except (KeyError, IndexError):
                continue
            new_att = model.DiscoveredAttribute(host.id, att_type)
            new_att.display_name = ipaddress
            new_att.index = idx
            new_att.set_field('max_connections', values[2][idx])
            new_att.set_field('hostname', values[4][idx])
            try:
                if values[3][idx] != '2':
                    new_att.admin_down()
            except (KeyError, IndexError):
                new_att.admin_unknown()
            try:
                if values[5][idx] != '2':
                    new_att.oper_down()
            except (KeyError, IndexError):
                new_att.oper_unknown()
            rservers[idx] = new_att
    dobj.discover_callback(host.id, rservers)


def discover_alteon_realservices(dobj, att_type, host):
    oids = (
            (1,3,6,1,4,1,1872,2,1,9,2,4,1,1),
            (1,3,6,1,4,1,1872,2,1,9,2,4,1,2), #service
            (1,3,6,1,4,1,1872,2,1,9,2,4,1,3), #server
            (1,3,6,1,4,1,1872,2,1,9,2,4,1,5), #port
            (1,3,6,1,4,1,1872,2,1,9,2,4,1,6), #oper state
            (1,3,6,1,4,1,1872,2,1,5,2,1,2), #real server IP
            (1,3,6,1,4,1,1872,2,1,5,2,1,10), #real server state
            (1,3,6,1,4,1,1872,2,1,5,5,1,5), # virt server dname
            (1,3,6,1,4,1,1872,2,1,5,5,1,8), # virt server hname
            )
    return dobj.snmp_engine.get_table(
        host, oids, cb_alteon_realservices,
        oid_trim=1, dobj=dobj, att_type=att_type)

def cb_alteon_realservices(values, error, host, dobj, att_type):
    rservices = {}
    if values is not None:
        for key,virt_server in values[0].items():
            try:
                service_idx = values[1][key]
                real_server = values[2][key]
                port = values[3][key]
                ipaddress = values[5][key]
            except KeyError:
                continue

            new_att = model.DiscoveredAttribute(host.id, att_type)
            new_att.display_name = '{}:{}'.format(ipaddress, port)
            new_att.index = '{}.{}.{}'.format(virt_server, service_idx, real_server)
            new_att.set_field('ipaddress', ipaddress)
            new_att.set_field('port', port)
            new_att.set_field('real_server', real_server)
            try:
                if values[4][key] != '2':
                    new_att.oper_down()
            except (KeyError, IndexError):
                new_att.oper_unknown()
            try:
                if values[6][key] != '2':
                    new_att.admin_down()
            except (KeyError, IndexError):
                new_att.admin_unknown()
            rservices[new_att.index] = new_att
    dobj.discover_callback(host.id, rservices)


def discover_alteon_virtualservers(dobj, att_type, host):
    oids = (
            (1,3,6,1,4,1,1872,2,1,5,5,1,1), #index
            (1,3,6,1,4,1,1872,2,1,5,5,1,2), #ipaddress
            (1,3,6,1,4,1,1872,2,1,5,5,1,4), #state
            (1,3,6,1,4,1,1872,2,1,5,5,1,5), #dname
            (1,3,6,1,4,1,1872,2,1,5,5,1,8), #hname
            )
    return dobj.snmp_engine.get_table(
        host, oids, cb_alteon_virtualservers, oid_trim=1,
        dobj=dobj, att_type=att_type)


def cb_alteon_virtualservers(values, error, host, dobj, att_type):
    vservers = {}
    if values is not None:
        for key,idx in values[0].items():
            try:
                ipaddress = values[1][key]
            except KeyError:
                continue
            try:
                dname = values[3][key]
                hname = values[4][key]
            except KeyError:
                servername = 'unknown'
            else:
                servername = '{}.{}'.format(hname, dname)

            new_att = model.DiscoveredAttribute(host.id, att_type)
            new_att.display_name = ipaddress
            new_att.index = idx
            new_att.set_field('hostname', servername)
            new_att.set_field('ipaddress', ipaddress)
            try:
                if values[2][key] != '2':
                    new_att.oper_down()
            except KeyError:
                new_att.oper_unknown()
            vservers[idx] = new_att
    dobj.discover_callback(host.id, vservers)
