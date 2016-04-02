# -*- coding: utf-8 -*-
"""Test suite for Host Information discovery """

from nose.tools import assert_true

from rnms.tests.att_discovery import AttDiscTest
from rnms.lib.discovery.plugins.attributes.host_information import \
    discover_host_information, cb_match_host, cb_host_information,\
    cb_host_devtable


class TestHostInfo(AttDiscTest):
    __ad_parameters__ = '311'

    def test_disc_ok(self):
        """ Disc hostinfo calls SNMP str """
        assert_true(discover_host_information(*self.discover_args))
        self.assert_snmp_str_called()

    def test_cb_none(self):
        """ CbDisc match_host with none """
        self.check_callback_none(cb_match_host)

    def test_cb_empty(self):
        """ CBdisc match_host with empty reply """
        self.callback(cb_match_host, "")
        self.assert_callback({})

    def test_cb_match_found(self):
        """ CBdisc match_host with found item """
        self.callback(cb_match_host, "1.3.6.1.4.1.311")
        self.assert_snmp_list_called()

    def test_cb2_none(self):
        """ CbDisc host_info with none """
        self.check_callback_none(cb_host_information)

    def test_cb2_empty(self):
        """ CBdisc host_info with empty reply """
        self.check_callback_empty_list(cb_host_information, 4)

    def test_cb2_ok(self):
        """ CBdisc host_info with correct values """
        self.callback(cb_host_information,
                      ('blah', 'admin', 'hostname', 'location'))
        self.assert_snmp_many_called()

    def test_cb_devtable_none(self):
        """ CBdisc host devtable with None """
        cb_host_devtable(None, None, self.dobj, self.test_host,
                         self.discovered_attribute)
        self.assert_callback({'1': self.discovered_attribute})

    def test_cb_devtable_ok(self):
        """ CBdisc host devtable with values """
        values = (
            ('1.3.6.1.2.1.25.3.1.3',),
            ('1.3.6.1.2.1.25.3.1.42',),
            ('1.3.6.1.2.1.25.3.1.33',),
            ('1.3.6.1.2.1.25.3.1.3',),
            ('1.3.6.1.2.1.25.3.9.3',),
            )
        cb_host_devtable(values, None, self.dobj, self.test_host,
                         self.discovered_attribute)
        self.assert_callback({'1': self.discovered_attribute})
