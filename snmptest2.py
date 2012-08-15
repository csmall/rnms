
from rnms.lib.snmp import SnmpEngine
from asyncore import poll

eng = SnmpEngine()

class DummyHost():
    mgmt_address = ''
    community_ro = {}
    def __init__(self, ip):
        self.mgmt_address = ip
host = DummyHost('127.0.0.1')
host.community_ro = { 0: 2, 1: "public"}

def my_cb(value, host, kwargs,error=None):
    print "------\n callback\nValue:{0}\nHost:  {1}".format(value, host.mgmt_address)
    print kwargs
    if error is not None:
        print "SNMP Error: {0}".format(error)
    print "------"

eng.get(host, (4,3,6,1,2,1,1,1,0), my_cb,foo="bar")
while (eng.poll()):
    pass
print "test done"
