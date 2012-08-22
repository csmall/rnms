
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
    #eng.get_str(host, (1,3,6,1,2,1,1,1,0), my_cb,go="in func cb2")


def my_cb(value, host, kwargs,error=None):
    print "------\n callback\nHost: {0}".format(host.mgmt_address)
    if type(value) == dict:
        for oid,val in value.items():
            print "{0} = {1}".format(oid, val)
    else:
        print "Value:{0}".format(value)
    print kwargs
    if error is not None:
        print "SNMP Error: {0}".format(error)
    print "------"

#eng.get_str(host, (1,3,6,1,2,1,1,2,0), my_cb,foo="bar",eng=eng)
#eng.get_int(deadhost, (1,3,6,1,2,1,1,1,0), my_cb,default=42, foo="bar2")
#eng.get_str(host, (4,3,6,1,2,1,1,1,0), my_cb,foo="error?")
eng.get_int(host, (1,3,6,1,2,1,2,1,0), my_cb)
eng.get_table(host,(1,3,6,1,2,1,2,2,1,1), my_cb, table_trim=1) 
while (eng.poll()):
    pass
print "test done"
