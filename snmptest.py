# SET Command Generator 
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from asyncore import poll
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
from time import time

# Protocol version to use
pMod = api.protoModules[api.protoVersion1]

# Build PDU
reqPDU =  pMod.GetRequestPDU()
pMod.apiPDU.setDefaults(reqPDU)
pMod.apiPDU.setVarBinds(
reqPDU, (((4,3,6,1,2,1,1,1,0), pMod.Null()),
    ((1,3,6,1,2,1,1,3,0), pMod.Null()))
)

# Build message
reqMsg = pMod.Message()
pMod.apiMessage.setDefaults(reqMsg)
pMod.apiMessage.setCommunity(reqMsg, 'public')
pMod.apiMessage.setPDU(reqMsg, reqPDU)

def cbTimerFun(timeNow, startedAt=time()):
    print "ding {0} start {1}\n".format(timeNow,startedAt)
    if timeNow - startedAt > 3:
        transportDispatcher.jobFinished(1)
        print "request timed out"

def cbRecvFun(transportDispatcher, transportDomain, transportAddress,
        wholeMsg, reqPDU=reqPDU):
    while wholeMsg:
        rspMsg, wholeMsg = decoder.decode(wholeMsg, asn1Spec=pMod.Message())
    rspPDU = pMod.apiMessage.getPDU(rspMsg)
    # Match response to request
    if pMod.apiPDU.getRequestID(reqPDU)==pMod.apiPDU.getRequestID(rspPDU):
        # Check for SNMP errors reported
        errorStatus = pMod.apiPDU.getErrorStatus(rspPDU)
        if errorStatus:
            print errorStatus.prettyPrint()
        else:
            for oid, val in pMod.apiPDU.getVarBinds(rspPDU):
                print '%s = %s' % (oid.prettyPrint(), val.prettyPrint())
        transportDispatcher.jobFinished(1)
    return wholeMsg


transportDispatcher = AsynsockDispatcher()
transportDispatcher.registerTransport(
        udp.domainName, udp.UdpSocketTransport().openClientMode()
        )
transportDispatcher.registerRecvCbFun(cbRecvFun)
transportDispatcher.registerTimerCbFun(cbTimerFun)
transportDispatcher.sendMessage(
        encoder.encode(reqMsg), udp.domainName, ('172.16.242.199', 161)
)
transportDispatcher.jobStarted(1)
transportDispatcher.sendMessage(
        encoder.encode(reqMsg), udp.domainName, ('localhost', 161)
)
transportDispatcher.jobStarted(1)
working=True
while transportDispatcher.jobsArePending() or transportDispatcher.transportsAreWorking():
    poll(0.5, transportDispatcher.getSocketMap())
    transportDispatcher.handleTimerTick(time())
    print "ding2"

#transportDispatcher.runDispatcher()
print "goo"
transportDispatcher.closeDispatcher()