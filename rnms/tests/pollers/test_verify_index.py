# -*- coding: utf-8 -*-
"""Test suite for verify index Pollers """
from nose.tools import eq_

from rnms.tests.pollers import PollerTest

from rnms.lib.poller.plugins.verify_index import filter_storage_name,\
    poll_verify_storage_index, cb_storage_index


class TestStorageName(PollerTest):

    def test_filter_empty(self):
        """ filter_storage_name with empty returns empty """
        eq_(filter_storage_name(''), '')

    def test_filter_unix(self):
        """ filter_storage_name with unix entry returns same """
        eq_(filter_storage_name('/dev/md0'), '/dev/md0')

    def test_filter_junos(self):
        """ filter_storage_name with junos entry returns filtered string """
        eq_(filter_storage_name('/dev/md0, mounted on: /junos'), '/junos')


class TestVerifyIndexPoller(PollerTest):
    def test_poll_storage_ok(self):
        """ poll_verify_storage_index returns True """
        eq_(poll_verify_storage_index(self.poller_buffer, **self.test_kwargs),
            True)
        self.assert_get_str_called((1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 3, 1),
                                   cb_storage_index)

    def test_poll_storage_noindex(self):
        """ poll_verify_storage_index with no attribute index returns False """
        self.test_attribute.index = ''
        eq_(poll_verify_storage_index(self.poller_buffer, **self.test_kwargs),
            False)
