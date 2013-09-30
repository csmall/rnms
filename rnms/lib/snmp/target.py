import socket

from pysnmp.entity.rfc3413.oneliner import target, cmdgen
from pysnmp.carrier.asynsock.dgram.udp import UdpSocketTransport
from pysnmp.carrier.asynsock.dgram.udp6 import Udp6SocketTransport

class MySocketTransport(UdpSocketTransport):
    zmq_core = None
    def registerSocket(self, sockMap=None):
        print 'reg'
        self.zmq_core.register_sock(self.socket.fileno(), self)

    def unregisterSocket(self, sockMap=None):
        self.zmq_core.unregister_sock(self.socket.fileno())

class My6SocketTransport(Udp6SocketTransport):
    zmq_core = None
    def registerSocket(self, sockMap=None):
        print 'reg6'
        self.zmq_core.register_sock(self.socket.fileno(), self)

    def unregisterSocket(self, sockMap=None):
        self.zmq_core.unregister_sock(self.socket.fileno())

class MyUdpTransportTarget(cmdgen.UdpTransportTarget):
    protoTransport = MySocketTransport
    def __init__(self, zmq_core, transportAddr, **kwargs):
        self.zmq_core = zmq_core
        cmdgen.UdpTransportTarget.__init__(self, transportAddr, **kwargs)

    def openClientMode(self):
        self.transport = self.protoTransport().openClientMode()
        self.transport.zmq_core = self.zmq_core
        return self.transport

class MyUdp6TransportTarget(target.Udp6TransportTarget):
    protocolTransport = My6SocketTransport
    zmq_core = None

    def __init__(self, zmq_core, transportAddr, **kwargs):
        self.zmq_core = zmq_core
        target.Udp6TransportTarget.__init__(self, transportAddr, **kwargs)

    def openClientMode(self):
        self.transport = self.protoTransport().openClientMode()
        self.transport.zmq_core = self.zmq_core
        return self.transport

def get_transport_target(zmq_core, host_addr):
    """ Return the correct transport target for
    the given host """
    try:
        addrinfo = socket.getaddrinfo(host_addr,0)[0]
    except socket.gaierror:
        return None
    if addrinfo[0] == socket.AF_INET:
        return  MyUdpTransportTarget(zmq_core, (host_addr, 161))
    elif addrinfo[0] == socket.AF_INET6:
        return  MyUdp6TransportTarget(zmq_core, (host_addr, 161))
    raise ValueError('unknown transport type')

