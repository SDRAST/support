"""
net_ID - module with function for task ID variable names and server names.

task programs (both server and client) are identified by numeric IDs (int)
server programs are identified by ASCII names (str)

There is some indirection that this routine handles.  net_appl.h
associates the numeric IDs with generic names.  net_rdc.h associates
some project-specific names with the generic names.

See /usr/local/pkg/rdc-dev/lib/net_rdc.h for details
"""
import re
import logging
from support.lists import list_dictionary

module_logger = logging.getLogger(__name__)

def get_net_IDs():
   """Returns two dictionaries which Associate symbolic server and
   task names with their values (string and int respective).
   net_appl.h defines 23 servers and 33 tasks (clients). The server
   symbolic names and their values, as well as the corresponding
   task (client) IDs are:
   ------ Server ---------   ---- Client -----      IP
   Name Symbol   Name        ID Symbol      ID     Port
   -----------   ---------   ----------    ---     ----
   SGW_SRV       sgw_srv     SGW_TASK        1     7001
   CTL_SRV       ctl_srv     CTL_TASK        2     7002
   MON_SRV       mon_srv     MON_TASK        3     7003
   APP_SRV1      app_srv1    SRV1_TASK     101     7004
   APP_SRV2      app_srv2    SRV2_TASK     102     7005
   APP_SRV3      app_srv3    APP1_TASK       4     7006
     ...           ...          ...        ...
   APP_SRV10     app_srv10   APP8_TASK      11     7013
   APP_SRV11     app_srv11   SRV11_TASK    111     7014
     ...           ...             ...         ...
   APP_SRV20     app_srv20   SRV20_TASK    120     7023
   Also, the following additional clients are defined:
                             ID Symbol       ID
                             ----------      --
                             ANY_TASK         0
                             APP9_TASK       12
                             APP10_TASK      13
                                 ...         ..
                             APP17_TASK      20
   If there is a pattern here, Thang will have to explain it.

   Furthermore, for the DSN Science R&D Control System, the above
   symbolic names have been mapped as follows:
           Servers                          Clients
     RDC           generic             RDC           generic
   --------        --------         ---------       ---------
   ANT_SRV1        APP_SRV3         ANT_TASK1       APP1_TASK
   ANT_SRV2        APP_SRV4         ANT_TASK2       APP2_TASK
   ANT_SRV3        APP_SRV5         ANT_TASK3       APP3_TASK
   ANT_SRV4        APP_SRV6         ANT_TASK4       APP4_TASK
   ANT_SRV5        APP_SRV7         ANT_TASK5       APP5_TASK
   ANT_SRV6        APP_SRV8         ANT_TASK6       APP6_TASK
   ANT_SRV7        APP_SRV9         ANT_TASK7       APP7_TASK
   ANT_SRV8        APP_SRV10        ANT_TASK8       APP8_TASK
   RAC_SRV         APP_SRV2         RAC_TASK        SRV2_TASK
   SPEC_SRV        APP_SRV11        SPEC_TASK       SRV11_TASK
                                    CMD_TASK        APP9_TASK
                                    PCFS_TASK       APP10_TASK
                                    RCTL_TASK       APP11_TASK
                                    DMON_TASK       APP12_TASK
   The latter four are for programs that have no server function.
   For example, RCTL_TASK is the task controlling the SPEC_SRV
   and PCFS_TASK may control an ANT_SRVx.
   """
   net_task = {}
   net_srvr = {}
   net_proj = open('/usr/local/pkg/rdc/include/net_rdc.h',
                   'r')
   lines = net_proj.readlines()
   net_proj.close()
   for line in lines:
      if re.search(chr(35)+'define',line):
         if re.search('_TASK',line):
            words = line.strip().split()
            net_task[words[1]] = words[2]
         elif re.search('_SR',line):
            words = line.strip().split()
            net_srvr[words[1]] = words[2]
   module_logger.debug("From net_rdc.h net_task has\n%s",
                       list_dictionary(net_task))
   module_logger.debug("From net_rdc.h 'net_srvr' has \n%s",
                       list_dictionary(net_srvr))
   # associate all the Net Services symbolic task and server names with
   # their values
   task_id = {}
   srvr_id = {}
   net_appl = open('/usr/local/pkg/netsrv/include/net_appl.h','r')
   lines = net_appl.readlines()
   net_appl.close()
   for line in lines:
      if re.search(chr(35)+'define',line):
         # the following tricky regexp is needed to avoid picking up
         # #define MAXTASKS        (APP17_TASK+1)
         # which would otherwise catch APP17_TASK
         if re.search("_TASK[ \t]",line):
            words = line.strip().split()
            task_id[words[1]] = int(words[2])
         elif re.search("_SR",line):
            words = line.strip().split()
            srvr_id[words[1]] = words[2].strip('"')
   module_logger.debug("From net_appl.h\ntask_id has\n%s\nsrvr_id has\n%s",
                        list_dictionary(task_id),
                        list_dictionary(srvr_id))
   # associate all the project-defined task and server symbolic names with
   # their values
   for id in net_task.keys():
      temp = net_task[id]
      net_task[id] = int(task_id[temp])
      task_id.pop(temp)
   for id in net_srvr.keys():
      temp = net_srvr[id]
      net_srvr[id] = srvr_id[temp]
      srvr_id.pop(temp)

   # add any remaining Net Services symbolic names to the project names
   for id in task_id.keys():
      net_task[id] = task_id[id]
   for id in srvr_id.keys():
      net_srvr[id] = srvr_id[id]
   return net_srvr, net_task

if __name__ == "__main__":
   mylogger = logging.getLogger()
   mylogger.setLevel(logging.INFO)
   net_srvr, net_task = get_net_IDs()
   mylogger.info("Result:\nnet_task has\n%s\nnet_srvr has\n%s",
                  list_dictionary(net_task),
                  list_dictionary(net_srvr))
