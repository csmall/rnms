# -*- coding: utf-8 -*-
#
# This file is part of the Rosenberg NMS
#
# Copyright (C) 2013 Craig Small <csmall@enc.com.au>
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
"""Test suite for Cisc Accounting Pollers """
from nose.tools import eq_

from rnms import model
from rnms.tests.pollers import PollerTest
from rnms.lib import states

from rnms.lib.pollers.cisco_accounting import poll_cisco_accounting, set_acct_checkpoint, get_acct_table

class NOTestCiscoAcctPoller(PollerTest):

    def test_poll_nocomm(self):
        """ poll_cisco_accounting with no RW community returns None """
        self.test_host.community_rw = None
        eq_(poll_cisco_accounting(self.poller_buffer, '', **self.test_kwargs), True)
        self.assert_callback(None)

    def test_poll_ok(self):
        """ poll_cisco_accounting calls snmp engine ok """
        eq_(poll_cisco_accounting(self.poller_buffer, '', **self.test_kwargs), True)
        self.assert_get_int_called(set_acct_checkpoint, oid=(1,3,6,1,4,1,9,2,4,11,0))

    # acct_checkpoint
    def test_acct_checkpoint_none(self):
        """ set_acct_checkpoint with None callback None """
        set_acct_checkpoint(None, None, **self.test_kwargs)
        self.assert_callback(None)

    def test_acct_checkpoint_ok(self):
        """ set_acct_checkpoint calls snmp set """
        set_acct_checkpoint('42', None, **self.test_kwargs)
        self.assert_snmp_set_called((1,3,6,1,4,1,9,2,4,11,0) , get_acct_table, 42)
