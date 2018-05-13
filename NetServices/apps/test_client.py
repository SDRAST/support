"""
demo client that works with test_server.py

Example (with test_client.py)::
  python test_client.py
  DEBUG:support.NetServices.net_IDs:From net_rdc.h net_task has
  14 items
  ANT_TASK1 APP1_TASK
  ...
  ANT_TASK8 APP8_TASK
  CMD_TASK  APP9_TASK
  DMON_TASK APP12_TASK
  PCFS_TASK APP10_TASK
  RAC_TASK  SRV2_TASK
  RCTL_TASK APP11_TASK
  SPEC_TASK SRV11_TASK
  
  DEBUG:support.NetServices.net_IDs:From net_rdc.h 'net_srvr' has
  10 items
  ANT_SRV1  APP_SRV3
  ...
  ANT_SRV8  APP_SRV10
  RAC_SRV APP_SRV2
  SPEC_SRV  APP_SRV11
  
  DEBUG:support.NetServices.net_IDs:From net_appl.h
  task_id has
  33 items
  ANY_TASK  0
  APP10_TASK  13
  ...
  APP17_TASK  20
  APP1_TASK 4
  ...  APP9_TASK 12
  CTL_TASK  2
  MON_TASK  3
  SGW_TASK  1
  SRV11_TASK  111
  ...
  SRV19_TASK  119
  SRV1_TASK 101
  SRV20_TASK  120
  SRV2_TASK 102
  
  srvr_id has
  23 items
  APP_SRV1  app_srv1
  ...
  APP_SRV20 app_srv20
  CTL_SRV ctl_srv
  MON_SRV mon_srv
  SGW_SRV sgw_srv
  
  INFO:root: Connected with socket 3
   Your message?: hello
  DEBUG:root: Sent message
   Your message?: load
  DEBUG:root: Sent message
   Your message?: Exit
  DEBUG:root: Sent message
  DEBUG:root: Closed connection
"""
import logging
from support.NetServices import *
from support.NetServices.net_IDs import get_net_IDs

logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger()

net_srvr, net_task = get_net_IDs()

socket = net_connect("ctl_srv","localhost",net_task['ANT_TASK5'],BLOCKING)

running = True
if socket > 0:
   mylogger.info(" Connected with socket %s",socket)
   while running:
      msg = raw_input(" Your message?: ")
      sent = net_send(socket,msg,BLOCKING)
      mylogger.debug(" Sent message")
      if msg == "Exit":
         net_close(socket)
         mylogger.debug(" Closed connection")
         running = False
         socket = 0
else:
   mylogger.error("Connection failed: %s",socket)
