# -*- coding: utf-8 -*-
"""
Functional test suite for the NTP client

"""
import mock

from nose.tools import eq_

from rnms.lib.ntpclient import NTPClient
from rnms.lib import zmqcore


class DummyHost(object):
    mgmt_address = ''
    community_ro = {}

    def __init__(self, ip):
        self.mgmt_address = ip


def my_cb_peer_by_id(response_packet, error, host, **kwargs):
    if response_packet.assoc_data == {}:
        kwargs['obj'].results['noid'] = response_packet.assoc_id
    else:
        kwargs['obj'].results = response_packet.assoc_data
    return response_packet.more == 1


def my_cb_peers(response_packet, error, host, **kwargs):
    if len(response_packet) == 0:
        kwargs['obj'].results['none'] = True
        return
    for a_id, a_selection in response_packet:
        if a_selection == 6:
            kwargs['obj'].ntp_client.get_peer_by_id(host,
                                                    a_id, my_cb_peer_by_id,
                                                    **kwargs)
    return False


class TestNTP(object):
    """ Base unti for NTP client testing """

    def setUp(self):
        self.zmq_core = zmqcore.ZmqCore()
        self.ntp_client = NTPClient(self.zmq_core, mock.Mock())
        self.results = {}

    def poll(self):
        while self.ntp_client.poll():
            self.zmq_core.poll(0.2)

    def NOtest_timeout(self):
        """ NTP query to non-existent host should timeout and give
        empty response back """
        host = DummyHost('10.10.0.254')
        self.ntp_client.get_peers(host, my_cb_peers, obj=self)
        self.ntp_client.get_peers(host, my_cb_peers, obj=self)
        self.poll()
        eq_(self.results['none'], True)

    def NOtest_success(self):
        """ Querying list and specific assoc gives assoc details """
        host = DummyHost('127.0.0.1')
        self.ntp_client.get_peers(host, my_cb_peers, obj=self)
        self.poll()
        assert('srcadr' in self.results)
        assert('filtdelay' in self.results)  # in second packet

    def NOtest_ipv6(self):
        """ Query using ipv6 """
        host = DummyHost('::1')
        self.ntp_client.get_peers(host, my_cb_peers, obj=self)
        self.poll()
        assert('srcadr' in self.results)
        assert('filtdelay' in self.results)  # in second packet

    def NOtest_no_assoc(self):
        """ Query for non-exist assoc details should return empty """
        fake_assoc_id = 65535  # hopefully anyhow
        host = DummyHost('127.0.0.1')
        self.ntp_client.get_peer_by_id(host, fake_assoc_id,
                                       my_cb_peer_by_id, obj=self)
        self.poll()
        assert('noid' in self.results)
        eq_(self.results['noid'], fake_assoc_id)
