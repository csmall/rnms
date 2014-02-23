# -*- coding: utf-8 -*-
"""Test suite for Buffer Poller """
from nose.tools import eq_

from rnms import model
from rnms.tests.pollers import PollerTest
from rnms.lib import states

from rnms.lib.poller.plugins.buffer import poll_buffer

class TestBufferPoller(PollerTest):

    def setUp(self):
        super(TestBufferPoller, self).setUp()
        self.poller_buffer = {'status': 'up', 'maximum': 100, 'minimum': 0 }

    def test_poll_empty(self):
        """ poll_buffer with no parameters returns False """
        eq_(poll_buffer(self.poller_buffer, '', **self.test_kwargs), False) 

    def test_poll_single_hit(self):
        """ poll_buffer with single hit returns value """
        eq_(poll_buffer(self.poller_buffer, 'status', **self.test_kwargs), True) 
        self.assert_callback(['up',])
    
    def test_poll_multi_hit(self):
        """ poll_buffer with two hits returns values """
        eq_(poll_buffer(self.poller_buffer, 'status,maximum', **self.test_kwargs), True) 
        self.assert_callback(['up',100])
    
    def test_poll_miss_then_hit(self):
        """ poll_buffer with one hit and one miss returns value """
        eq_(poll_buffer(self.poller_buffer, 'foo,maximum', **self.test_kwargs), True) 
        self.assert_callback([None,100])
