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
from pysnmp.entity.rfc3413.oneliner import cmdgen
REQUEST_SINGLE = 0
REQUEST_LIST = 1
REQUEST_TABLE = 2
REQUEST_MANY = 3

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

class SNMPRequest(object):
    """
    Class for filling in SNMP requests.  There may be multiple OIDs
    within the same request, for speed
    """

    replyall = False
    with_oid = None

    id = None

    def __init__(self, host, community):
        self.host = host
        self.oids = []
        self.varbinds = None
        self.table_oids = None
        self.msg = None
        self.community = community
        self.request_type = REQUEST_SINGLE

    def __repr__(self):
        return "<SNMPRequest Host:{0} #oids:{1}>".format(
            self.host.mgmt_address, len(self.oids))

    def add_oid(self, oid, callback, data=None, default=None, filt=None,
                value=None):
        """
        Add another OID to this request, there can be multiple queries
        to the same host
        """
        self.oids.append({'oid': oid, 'callback': callback, 'data': data,
                          'default': default, 'filter': filt,
                          'rawoid': cmdgen.MibVariable(oid),
                          'value': value })

    def set_table(self):
        self.request_type = REQUEST_TABLE
        self.replyall = True
    
    def set_many(self):
        self.request_type = REQUEST_MANY
        self.replyall = True

    def is_table(self):
        """ Return True if request is table request """
        return self.request_type == REQUEST_TABLE

    def is_many(self):
        """ Return True if request is many request """
        return self.request_type == REQUEST_MANY

    def set_replyall(self, flag):
        """
        By default, each OID will have its own callback.  Setting this
        flag means that the first OID's callback will be used and it
        will get the whole table.
        This is similar to what happens with a get_table() except it is
        specific items
        """
        self.replyall = flag

    def callback_default(self, error=None):
        """
        Fire off all the callbacks with the default value
        """
        if self.replyall:
            req = self.oids[0]
            if req['data'] is None:
                req['callback'](req['default'], error, host=self.host)
            else:
                req['callback'](req['default'], error, host=self.host, 
                                **(req['data']))
        else:
            for req in self.oids:
                if req['data'] is None:
                    req['callback'](req['default'], error, host=self.host)
                else:
                    req['callback'](req['default'], error, host=self.host,
                                    **(req['data']))

    def callback_table(self):
        """
        Reply back to the caller with a SNMP table
        """
        if self.replyall:
            self.oids[0]['callback'](
                self.varbinds, None, host=self.host,
                **self.oids[0]['data'])
        else:
            for idx in len(self.oids):
                self.oids[idx]['callback'](
                    self.varbinds[idx], None, host=self.host,
                    **self.oids[idx]['data'])

    def callback_single(self, req_oid, value, error=None):
        """
        Fire off the callack with the given value
        """
        if req_oid['filter'] is not None:
            try:
                value = VALUE_FILTERS[req_oid['filter']](value)
            except KeyError:
                pass
        if req_oid['data'] is None:
            req_oid['callback'](value, error, host=self.host)
        else:
            req_oid['callback'](value, error, host=self.host,
                                **(req_oid['data']))

    def is_get(self):
        """ Return True if Request is a SNMP get """
        return self.request_type == REQUEST_SINGLE

    def is_getnext(self):
        """ Return True if Request is a SNMP getnext """
        return self.request_type in (REQUEST_TABLE,REQUEST_MANY) and self.community == 1

    def is_getbulk(self):
        """ Return True if Request is a SNMP getbulk """
        return self.request_type in (REQUEST_TABLE,REQUEST_MANY) and self.community != 1

