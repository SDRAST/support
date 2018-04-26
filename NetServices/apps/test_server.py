"""
demo server for Net Services

After initialization, the basic procedure is as follows::
   *  Set the bits in 'readfds' for all the sockets of interest.
   *  Call 'select' which returns with the bits set for all the sockets that have data.
   *  Process the tasks for all the pending ports.
In summary::
   #  FD_ZERO - clear 'readfds'
   #  loop over FD_SET for all sockets of interest
   #  call 'select'
   #  Loop over FD_ISSET to process the pending sockets

Initially, the only sockets which are active are::
   0 - stdin
   1 - stdout
   2 - stderr
   3 - listenfd, the one on which new connections are accepted.

If 'select' shows data at the listenfd socket, client_accept() is
invoked. In client_accept(), net_accept() establishes a TCP connection
and assigns a file descriptor. Then, net_getpeername() is used to
identify the client process. If the client process cannot be identified,
it is assumed to be an anonymous process (ANY_TASK).

Example (together with test_client.py)::
  python test_server.py
  DEBUG:__main__: ctl_srv listening at socket 3
  DEBUG:__main__:Checking 3 in [3]
  Requested mode is 0 type <type 'int'>
  net_accept returned 4
  which is type <type 'int'>
  DEBUG:__main__: New connection accepted at 4
  from localhost with process 8 at port 7002
  DEBUG:__main__:Checking 4 in [4]
  DEBUG:__main__: From 4 received: hello
  DEBUG:__main__:Checking 4 in [4]
  DEBUG:__main__: From 4 received: load
  DEBUG:__main__:Checking 4 in [4]
  DEBUG:__main__: From 4 received: Exit
  DEBUG:__main__: We are done.
"""

from support.NetServices import *
from support.NetServices.net_IDs import get_net_IDs
import sys
import logging

module_logger = logging.getLogger(__name__)
module_logger.setLevel(logging.DEBUG)

net_srvr, net_task = get_net_IDs()
diag = False

def server(serverID):
   read_list      = []
   write_list     = []
   exception_list = []
   my_socket = net_init(serverID)
   module_logger.debug(" ctl_srv listening at socket %s",my_socket)
   read_list.append(my_socket)
   if my_socket > 0:
      running = True
      timeout = 60
      while (running):
         read_waiting,write_waiting,exc_waiting = select.select(read_list,
            write_list, exception_list,timeout)
         if read_waiting == [] and write_waiting == [] and exc_waiting == []:
            module_logger.debug(" Nothing yet")
         else:
            for socket in read_waiting:
               module_logger.debug("Checking %s in %s",socket,read_waiting)
               if socket == my_socket:
                  new_socket = net_accept(socket,BLOCKING)
                  hostname,process_ID = get_peername(new_socket)
                  module_logger.debug(" New connection accepted at %s\nfrom %s with process %d at port %s",
                                      new_socket,
                                      hostname,
                                      process_ID,
                                      get_serverport(serverID))
                  read_list.append(new_socket)
               else:
                  length,msg = net_recv(socket,BLOCKING)
                  if length == 0:
                     module_logger.debug(" Client at %s disconnected",socket)
                     net_close(socket)
                     read_list.remove(socket)
                  else:
                     module_logger.debug(" From %s received: %s",socket,msg)
                     if msg == "Exit":
                        net_close(my_socket)
                        module_logger.debug(" We are done.")
                        sys.exit(0)
   else:
      
      if my_socket == -1:
         status = "due to system error"
      elif socket == -3:
         status = "because of bad endpoint name"
      module_logger.error("Failed to initialize a server %s", status)

if __name__ == "__main__":
   logging.basicConfig(level=logging.DEBUG)
   mylogger = logging.getLogger()
   server("ctl_srv")
