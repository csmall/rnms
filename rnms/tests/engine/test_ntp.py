# -*- coding: utf-8 -*-
"""
Functional test suite for the NTP client

"""
import socket
import asyncore

from nose.tools import assert_true, nottest, eq_

from rnms.lib.ntpclient import NTPClient, NTPControl

def my_callback_none(data, kwargs):
    kwargs['obj'].results['none']= True
    return False

def my_callback2(data, kwargs):
    if 'obj' not in kwargs:
        assert False
        return
    stats = kwargs['response_packet']
    stats.from_data(data)
    if stats.more == 0:
        kwargs['obj'].results = stats.assoc_data
    return stats.more == 1

def my_callback1(data, kwargs):
    if 'obj' not in kwargs:
        assert False
        return
    stats = kwargs['response_packet']
    stats.from_data(data)
    eq_(stats.response, 1)
    for assoc in stats.peers:
        if assoc.selection == 6:
            query_packet = NTPControl(opcode=2, sequence=1, assoc_id=assoc.assoc_id)
            kwargs['obj'].ntp_client.send_message(kwargs['sockaddr'],query_packet.to_data(), my_callback2, **kwargs)
    return stats.more == 1


class TestNTP(object):
    """ Base unti for NTP client testing """

    def setUp(self):
        self.ntp_client = NTPClient(socket.SOCK_DGRAM, timeout=2)
        self.results = {}

    def poll(self):
        while self.ntp_client.poll():
            asyncore.poll(3)

    def test_timeout(self):
        """ Test that the client times out after 10 secs"""
        addrinfo = socket.getaddrinfo('12.0.0.1', 123)[0]
        family, sockaddr = addrinfo[0], addrinfo[4]
        query_packet = NTPControl()
        self.ntp_client.send_message(sockaddr, query_packet.to_data(), my_callback_none, obj=self)
        self.poll()
        eq_(self.results['none'], True)

    def test_succ(self):
        """ Test that we get a NTP assoc data """
        addrinfo = socket.getaddrinfo('127.0.0.1', 123)[0]
        family, sockaddr = addrinfo[0], addrinfo[4]
        query_packet = NTPControl()
        response_packet = NTPControl()
        self.ntp_client.send_message(sockaddr, query_packet.to_data(), my_callback1, obj=self, sockaddr=sockaddr, response_packet=response_packet)
        self.poll()
        assert('srcadr' in self.results)
        assert('filtdelay' in self.results) # in second packet
