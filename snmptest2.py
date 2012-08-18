
from rnms.lib.snmp import SNMPEngine
from asyncore import poll
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("snmptest2")

eng = SNMPEngine(logger=logger)

class DummyHost():
    mgmt_address = ''
    community_ro = {}
    def __init__(self, ip):
        self.mgmt_address = ip
host = DummyHost('127.0.0.1')
host.community_ro = { 0: 2, 1: "public"}

deadhost = DummyHost("255.0.0.0")
deadhost.community_ro = { 0: 2, 1: "public"}

def my_cb2(value, host, kwargs, error=None):
    print "in my cb2, calling anohter request\n"
    eng = kwargs['eng']
    eng.get_str(host, (1,3,6,1,2,1,1,1,0), my_cb,go="in func cb2")


def my_cb(value, host, kwargs,error=None):
    print "------\n callback\nValue:{0}\nHost:  {1}".format(value, host.mgmt_address)
    print kwargs
    if error is not None:
        print "SNMP Error: {0}".format(error)
    print "------"

eng.get_str(host, (1,3,6,1,2,1,1,1,0), my_cb2,foo="bar",eng=eng)
eng.get_int(deadhost, (1,3,6,1,2,1,1,1,0), my_cb,default=42, foo="bar2")
eng.get_str(host, (4,3,6,1,2,1,1,1,0), my_cb,foo="error?")
while (eng.poll()):
    pass
print "test done"
