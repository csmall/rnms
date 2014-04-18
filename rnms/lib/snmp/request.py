# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2012-2014 Craig Small <csmall@enc.com.au>
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
import socket

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902

REQUEST_SINGLE = 0
REQUEST_LIST = 1
REQUEST_TABLE = 2
REQUEST_MANY = 3
REQUEST_SET = 4


# Filters
def filter_int(value):
    """ Coerce this given value into an integer """
    if value is None:
        return 0
    if type(value) is dict:
        value = value.popitem()[1]
    try:
        fvalue = int(value)
    except ValueError:
        fvalue = 0
    return fvalue


def filter_str(value):
    """ Coerce the value into a string """
    if value is None:
        return ""
    if type(value) is dict:
        value = value.popitem()[1]
    try:
        fvalue = str(value)
    except ValueError:
        fvalue = ""
    return fvalue

VALUE_FILTERS = {
    'int': filter_int,
    'str': filter_str
    }


def _get_host_transport(host_addr):
    """ Return the correct transport target for
    the given host """
    try:
        addrinfo = socket.getaddrinfo(host_addr, 0)[0]
    except socket.gaierror:
        return None
    if addrinfo[0] == socket.AF_INET:
        return cmdgen.UdpTransportTarget((host_addr, 161))
    elif addrinfo[0] == socket.AF_INET6:
        return cmdgen.Udp6TransportTarget((host_addr, 161))
    raise ValueError('unknown transport type')


class RequestOID(object):
    """ Holds each OID line for the requests """
    filter_ = None
    oid = None
    cb_data = None
    _value = None

    def __init__(self, oid, callback=None, value=None, **kw):
        self.oid = oid
        self.raw_oid = cmdgen.MibVariable(oid)
        self.cb_func = callback
        self.filter_ = kw.pop('filter', None)
        self.cb_data = kw
        self._value = value

    def callback_none(self, host, error=None):
        """ Fire callback returning None """
        self.callback(host, None, error)

    def callback(self, host, value, error=None):
        self.cb_func(value, error, host=host, **self.cb_data)

    def callback_single(self, host, value, error=None):
        if self.filter_ is not None:
            try:
                value = VALUE_FILTERS[self.filter_](value)
            except KeyError:
                pass
        self.callback(host, value, error)

    def is_prefix_of(self, other_oid):
        """ Return True if we are prefix of other_oid """
        return self.raw_oid.isPrefixOf(other_oid)


class SNMPRequest(object):
    """
    Class for filling in SNMP requests.  There may be multiple OIDs
    within the same request, for speed
    """
    _request_type = None
    transport_target = None
    _replyall = False
    with_oid = None
    _callback = None
    _cb_data = None

    id = None

    def __init__(self, host, community, callback=None, **kw):
        self.host = host
        self.transport_target = _get_host_transport(host.mgmt_address)
        self.oids = []
        self.varbinds = None
        self.table_oids = None
        self.msg = None
        self.community = community
        self._callback = callback
        self._cb_data = kw

    def __repr__(self):
        return "<SNMPRequest Host:{0} #oids:{1}>".format(
            self.host.mgmt_address, len(self.oids))

    def add_oid(self, oid, **kw):
        """
        Add another OID to this request, there can be multiple queries
        to the same host
        """
        self.oids.append(RequestOID(oid, **kw))

    def set_many(self):
        self._request_type = REQUEST_MANY
        self._replyall = True

    def is_table(self):
        """ Return True if request is table request """
        return self._request_type == REQUEST_TABLE

    def is_many(self):
        """ Return True if request is many request """
        return self._request_type == REQUEST_MANY

    def set_replyall(self, flag):
        """
        By default, each OID will have its own callback.  Setting this
        flag means that the first OID's callback will be used and it
        will get the whole table.
        This is similar to what happens with a get_table() except it is
        specific items
        """
        self._replyall = flag

    def is_replyall(self):
        """ Return true if reply once with for all OIDs """
        return self._replyall

    def callback_none(self, error=None):
        """ Fire off all the callbacks with None """
        if self._callback is not None:
            self._callback(None, error, host=self.host, **self._cb_data)
        else:
            for req in self.oids:
                req.callback_none(self.host, error)

    def callback_table(self):
        """
        Reply back to the caller with a SNMP table
        """
        if self._callback is not None:
            self._callback(self.varbinds, None, host=self.host,
                           **self._cb_data)
        else:
            for idx, oid in enumerate(self.oids):
                oid.callback(self.host, self.varbinds[idx], None)

    def callback_single(self, req_oid, value, error=None):
        """
        Fire off the callack with the given value
        """
        req_oid.callback_single(self.host, value, error)

    def is_get(self):
        """ Return True if Request is a SNMP get """
        return self._request_type == REQUEST_SINGLE

    def is_set(self):
        """ Return True if Request is a SNMP set """
        return self._request_type == REQUEST_SET

    def is_getnext(self):
        """ Return True if Request is a SNMP getnext """
        return self._request_type in (REQUEST_TABLE, REQUEST_MANY) and\
            self.community == 1

    def is_getbulk(self):
        """ Return True if Request is a SNMP getbulk """
        return self._request_type in (REQUEST_TABLE, REQUEST_MANY) and\
            self.community != 1

    def prepare(self, cmd_gen, callback):
        """ Create the command """
        if self.is_set():
            sending_oids = [(x.raw_oid, x._value) for x in self.oids]
        else:
            sending_oids = [x.raw_oid for x in self.oids]
        if self.is_getbulk():
            self.id = cmd_gen.bulkCmd(
                self.community.get_auth_data(),
                self.transport_target,
                0, 5,
                sending_oids,
                (callback, self)
            )
            return
        if self.is_getnext():
            self.id = cmd_gen.nextCmd(
                self.community.get_auth_data(),
                self.transport_target,
                sending_oids,
                (callback, self)
            )
            return
        if self.is_get():
            self.id = cmd_gen.getCmd(
                self.community.get_auth_data(),
                self.transport_target,
                sending_oids,
                (callback, self)
            )
            return
        if self.is_set():
            self.id = cmd_gen.setCmd(
                self.community.get_auth_data(),
                self.transport_target,
                sending_oids,
                (callback, self)
            )
            return
        raise NotImplementedError(
            'Request type {} not implemented'.format(self._request_type))


class SNMPGetTableRequest(SNMPRequest):
    """ Class for SNMP get returning a table """
    _request_type = REQUEST_TABLE
    _replyall = True


class SNMPGetRequest(SNMPRequest):
    """ Class for SNMP get single item """
    _request_type = REQUEST_SINGLE
    _replyall = False


class SNMPGetListRequest(SNMPRequest):
    """ Request class for SNMP lists """
    _request_type = REQUEST_SINGLE
    _replyall = True


class SNMPSetRequest(SNMPRequest):
    """
    Class for filling in SNMP set requests. """
    _request_type = REQUEST_SET
    _replyall = True

    def __init__(self, host, community, callback, **kw):
        self.callback = callback
        super(SNMPSetRequest, self).__init__(host, community,
                                             callback, **kw)

    def __repr__(self):
        return "<SNMPSetRequest Host:{0} #oids:{1}>".format(
            self.host.mgmt_address, len(self.oids))

    def set_int(self, oid, value):
        """ Add an Integer variable to set request """
        if not self.is_set():
            raise ValueError("Cannot set_int() a non SET request")
        self.oids.append(RequestOID(oid, self.callback,
                         rfc1902.Integer(value)))

    def set_str(self, oid, value):
        """ Add a String variable to a set request """
        if not self.is_set():
            raise ValueError("Cannot set_str() a non SET request")
        self.oids.append(RequestOID(oid, self.callback,
                         rfc1902.OctetString(value)))

    def set_ipaddr(self, oid, value):
        """ Add an IP Address variable to set request """
        if not self.is_set():
            raise ValueError("Cannot set_int() a non SET request")
        self.oids.append(RequestOID(oid, self.callback,
                         rfc1902.IpAddress(value)))
