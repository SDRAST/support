"""
This tests a connection to venus-eac1

This test must be done on a network that can resolve the server host name
"""
from support.NetServices import *
from support.NetServices.messages import *
from support.NetServices.net_IDs import get_net_IDs

import logging

logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger()

server,client = get_net_IDs()
me = client['ANY_TASK']
eac = net_connect(server['ANT_SRV1'],'venus-eac1',me,BLOCKING)

msg = encode('EAC', 'CMD', 'ONPOINT?', me)
if mylogger.level == logging.DEBUG:
   a,b,c,d = unpack('hcci',msg[0:8])
   mylogger.debug("Message: %s %s %s %s %s",
                  htons(a), str(b), str(c), htonl(d), msg[8:])
   mylogger.debug("Message length: %d",len(msg))
bytes_sent = net_send(eac,msg,BLOCKING)
if bytes_sent > 0:
   response = net_recv(eac,BLOCKING)
   mylogger.info(response)
else:
   mylogger.info("Empty response")