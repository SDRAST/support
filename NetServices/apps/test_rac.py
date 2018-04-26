"""
Test a Net Services connection to venus-rac1

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
rac = net_connect(server['RAC_SRV'],'venus-rac1', me, BLOCKING)

msg = encode('RAC', 'CMD', 'tsys', me)
if mylogger.level == logging.DEBUG:
   a,b,c,d = unpack('hcci',msg[0:8])
   mylogger.debug("Message: %s %s %s %s %s",
                   htons(a), str(b), str(c), htonl(d), msg[8:])
   mylogger.debug("Message length: %d",len(msg))
bytes_sent = net_send(rac,msg,BLOCKING)
mylogger.debug(" %d bytes sent",bytes_sent)
if bytes_sent > 0:
   num_bytes, response = net_recv(rac,BLOCKING)
   mylogger.info("%d bytes received", num_bytes)
   mylogger.info("%s", decode(response))
else:
   mylogger.warning("Empty response")
net_close(rac)