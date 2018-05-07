"""
This is a wrapper module for the Net Services library

Net Services is an inter-process TCP/IP protocol with a specific message
structure and identifications for servers and clients.

A 'task' is a program.  Both servers and clients have task (or program)
IDs.  Server program types are identified by names.

Task (Program) IDs
==================
my_process_id identifies the task ID of the program which invoked
the module. It is globally defined for the Net Services toolkit module.
my_process_id is part of a data structure of type serv_arr which
is used by clients to remember what ID they gave when they intially
connected to a server. my_process_id is initially -1.  This means that
the task invoking this module has not yet been specified.

In the net_connect command, a client specifies a "my_process_id" to
the server:

>>> net_connect  server_ID  server_host_name  my_process_ID

my_process_ID is an integer but is more typically specified as a module
global variable net_task(SOME_TASK) where SOME_TASK is one taken from a
list returned by:

>>> from netsrv.net_IDs import get_net_IDs
>>> net_srvr, net_task = get_net_IDs()

Failure to conform to these conventions will result in an error.

message ID
==========
Communication can be made even more secure by encoding the messages into
a particulat Net Services format.  See module 'messages' for details

Most significant 16 bits are subsystem ID.
The l.s. 8 bits are message type (1 - command, 2 - response).

Here's an example of how a message ID is constructed for a
subsystem XX::

   XX_CMD = (XX_ID  << 16) | CMD
   XX_RSP = (XX_ID  << 16) | RSP

Part of the message ID field is used for the message size.
Bits 8-15 contain a message size code which specifies the
length of the message as 128 * (size_code+1); thus, the
default message size is 128 bytes, and the maximum size
is 32768.  If other than the default of 0, the program must
insert this into the message ID field.

Note that there is a Net Services call to set a socket's I/O mode that
hasn't (yet) been provided with a wrapper function.)

Simple Example
==============

At the simplest level, Net Services is just another way to use IP and UNIX
domain sockets, like the Python socket module.  A typical sequence would be

SERVER                                 CLIENT
------------------------------------- --------------------------------------
from netsrv import *                  from netsrv import *

# Server Opens Socket
listen_socket = net_init("app_srv10")
                                      # Client Requests Connection
                                      my_process_id = 10
                                      srv_socket = net_connect("app_srv10",
                                                               "some_host",
                                                               my_process_ID,
                                                               BLOCKING)
# Server Accepts Connection
client_socket = net_accept(listen_socket,
                           NONBLOCKING)

                                      # Client sends message
                                      bytes_sent = net_send(srv_socket,
                                                            message,
                                                            BLOCKING)

# Server Sends Response
bytes_received, message = net_recv(client_socket,
                                   BLOCKING)

This example can be made more flexible by using select.select to check which
sockets need to be serviced.

Net Services differs from the socket module in that the servers and clients
must be correctly identified.  There are 23 allowed server names and 33
allowed client ID integers.
"""

from ctypes import cdll, create_string_buffer, byref
import select
import os
import logging

net_srv = cdll.LoadLibrary("/usr/local/lib/libnet_srv.so")
module_logger = logging.getLogger(__name__)

BLOCKING     =    0
NON_BLOCKING =    1

UNDEF        =    0
TCP          =    1
UDP          =    2
BRDCST       =    3

NET_MAX_FD   =  128
NET_BUFSIZE  = 4096

NEOF         =   0

SUCCESS      =   0
ERROR        =  -1;  SERROR = "system error"
NBADADDR     =  -2;  SBADADDR = "invalid IP address"
NBADENDPT    =  -3;  SBADENDPT = "bad server name"
NBADFD       =  -4;  SBADFD = "bad socket ID"
NBADHOST     =  -5;  SBADHOST = "invalid host"
NBADLENGTH   =  -6;  SBADLENGTH = "message length > maximum or < the minimum"
NBADMODE     =  -7;  SBADMODE = "invalid I/O mode"
NBADPROCESS  =  -8;  SBADPROCESS = "invalid process ID"
NSYNCERR     =  -9;  SSYNCERR = "incoming message boundaries are out of sync"
NWOULDBLOCK  = -10;  SWOULSBLOCK = "I/O mode is NON_BLOCKING but \
no data are present"

NBADARG      = -11

def process_error(status):
   """
   Reports on the Net Services error encountered

   @param status : error code
   @type  status : int
   """
   if status == ERROR:
      module_logger.error(" Net Services reports error %d",
                          net_srv.report_errno())
      module_logger.error( " meaning %s",
                          os.strerror(net_srv.report_errno()))
      raise SystemError(SERROR+': '+os.strerror(net_srv.report_errno()))
   elif status == NBADADDR:
      raise ValueError(SBADADDR)
   elif status == NBADENDPT:
      raise ValueError(SBADENDPT)
   elif status == NBADFD:
      raise ValueError(SBADFD)
   elif status == NBADHOST:
      raise ValueError(SBADHOST)
   elif status == NBADLENGTH:
      raise ValueError(SBADLENGTH)
   elif status == NBADMODE:
      raise ValueError(SBADMODE)
   elif status == NBADPROCESS:
      raise ValueError(SBADPROCESS)
   elif status == NSYNCERR:
      raise ValueError(SSYNCERR)
   elif status == NWOULDBLOCK:
      raise ValueError(SWOULDBLOCK)
   else:
      raise Exception("unknown error "+str(status))

def net_init(end_point):
   """
   Initializes a server.

   Only certain server names are allowed, as defined in net_appl.h::
    "sgw_srv"   - in the EAC, the gateway server,
    "ctl_srv"   - in the EAC, the controlling server
    "mon_srv"   - in the EAC, the monitor data server
    "app_srvXX" - where 1 <= XX <= 20, undefined
   Returns an integer socket number, not the same as the IP port number.
   The server will listen on this socket for connection attempts.
   On failure, it returns::
    -3 - when the endpoint name is not a valid endpoint.
    -1 - on a system call error, with errno containing the error indication.
   """
   if str(type(end_point)) == "<type 'str'>":
      socket = net_srv.net_init(end_point)
      if socket > 0:
         return socket
      else:
         process_error(socket)
   else:
      raise TypeError("argument is not a string")

def net_accept(listen_socket,mode):
   """
   Accept a connection

   Accepts a connection request on 'listen_socket' for I/O "mode" and
   establishes a full-duplex TCP connection with a client process that
   issued a net_connect() call to connect to a server.  The server must
   have previously called net_init() prior to calling net_accept().
   'mode' may be 0 (blocking) or 1 (non-blocking).  net_accept is invoked
   after 'net_select' reports a new client on 'listen_socket'.
   
   Return Values
   =============
     On success, net_accept() returns a file descriptor for the connected
   socket to be used in a subsequent net_send(), net_recv(), or net_close()
   call.
     On failure, it returns::
      -4   when listenfd is not a valid socket descriptor.
      -7   when the mode is not a valid I/O mode.
     -10   when the I/O mode is NON_BLOCKING and no connection requests are
           present to be accepted.
      -1   on a system call error, with errno containing the error indication.

    @param listen_socket : socket established with net_init()
    @type  listen_socket : socket instance

    @param mode : connection mode, blocking or non-blocking
    @type  mode : int

    @return: socket file descriptor (int) or error code
   """
   if (str(type(listen_socket)) == "<type 'int'>"):
      if (str(type(mode)) == "<type 'int'>"):
         print "Requested mode is",mode,"type",type(mode)
         socket = net_srv.net_accept(listen_socket,mode)
         print "net_accept returned",socket
         print "which is type",type(socket)
         if socket > 0:
            return socket
         else:
            process_error(socket)
      else:
         raise TypeError("mode is not an integer")
   else:
      raise TypeError("listen_socket is not an integer")

def net_connect(end_point, host, client_program, mode):
   """
   Initiates a connection request to a listening process

   It is called by a client process to establish a connection with a server.
   
   The client program identifies itself with any number between 0 and 20,
   here 1, 2, and 3 have specific meanings in the EAC context
   
   Once the connection request is accepted by a server calling net_accept(),
   messages can be exchanged over the established connection.
   
   Return Values
   =============
   On success, net_connect() returns a number for the connected socket
   to be used in a subsequent net_send(), net_recv(), or net_close() call.
   On failure, it returns::
      -3 -  when the endpoint name is not a valid endpoint.
      -5 -  when the hostname is not a valid hostname.
      -7 -  when the mode is not a valid I/O mode.
      -8 -  when the process name is not a valid process.
     -10 -  when the I/O mode is NON_BLOCKING and the connection cannot be completed immediately.
      -1 - on a system call error, with errno containing the error indication.

   @param endpoint : aserver name as defined in net_init
   @type  endpoint : str

   @param host : the name of the host with the server
   @type  host: str

   @param client_program : a number indicating the calling program
   @type  client_program : int

   @param mode : indicates BLOCKING or NON_BLOCKING
   @type  mode : int
   """
   if str(type(end_point)) == "<type 'str'>":
      if str(type(host)) == "<type 'str'>":
         if (str(type(client_program)) == "<type 'int'>"):
            if (str(type(mode)) == "<type 'int'>"):
               socket = net_srv.net_connect(end_point,
                                           host,
                                           client_program,
                                           mode)
               if socket > 0:
                  return socket
               else:
                  process_error(socket)
            else:
               raise TypeError("mode is not an integer")
         else:
            raise TypeError("client program is not an integer")
      else:
         raise TypeError("host is not a string")
   else:
      raise TypeError("endpoint is not a string")

def net_send(socket,message,mode):
   """
   sends a message to a connected endpoint

   This is a connection- oriented communication.  net_send() preserves
   message boundaries between the sender and receiver.
   
   Return Values
   =============
   On success, net_send() returns the number of bytes sent.  If a
   broken connection condition is detected, net_send() will return NEOF.
   On failure, it returns::
      -4 -  when sockfd is not a valid socket descriptor.
      -2 -  when the message pointer is not a valid pointer.
      -6 -  when the requested message length either exceeds the maximum
            length allowed or is less than the minimum required.
      -7 -  when the mode is not a valid I/O mode.
     -10 -  when the I/O mode is NON_BLOCKING and no messages could be sent
            immediately.  It is possible, however, that a partial message
            may have been sent when this error is returned.
      -1 -  on a system call error, with errno containing the error indication.
   """
   if (str(type(socket)) == "<type 'int'>"):
      if str(type(message)) == "<type 'str'>":
         length = len(message)
         if (str(type(mode)) == "<type 'int'>"):
            bytes_written = net_srv.net_send(socket,message,length,mode)
            if bytes_written > 0:
               return bytes_written
            else:
               process_error(bytes_written)
         else:
            raise TypeError("mode is not an integer")
      else:
         raise TypeError("message is not a string")
   else:
      raise TypeError("socket is not an integer")

def net_recv(socket,mode):
   """
   receives a message from a connected endpoint

   This in a connection-oriented communication.  net_recv() preserves message
   boundaries between the sender and receiver.  The received message will be
   placed into the array buf for up to maxlen bytes.  If the message is too
   long to fit in the supplied buffer, it will be truncated and the excess
   bytes discarded.
   
   Return Values
   =============
   On success, net_recv() returns the number of bytes received.  If a
   broken connection condition is detected, net_recv() will return
   NEOF.  On failure, it returns::
      -4 -  when sockfd is not a valid socket descriptor.
      -2 -  when the buffer pointer is not a valid pointer.
      -6 -  when the requested message length is less than
            the minimum length required.
      -7 -  when the mode is not a valid I/O mode.
      -9 -  when the incoming message boundaries are out of sync.
     -10 -  when the I/O mode is NON_BLOCKING and no messages were available
            to be received.  It is possible, however, that a partial message
            may have been received when this error is returned.
      -1 -  on a system call error, with errno containing the error indication.
   """
   if str(type(socket)) == "<type 'int'>":
      if (str(type(mode)) == "<type 'int'>"):
         buf = create_string_buffer(NET_BUFSIZE)
         num_received = net_srv.net_recv(socket,
                                        byref(buf),
                                        NET_BUFSIZE,
                                        mode)
         if num_received > 0:
            return num_received,buf.value
         else:
            process_error(num_received)
      else:
         raise TypeError("mode is not an integer")
   else:
      raise TypeError("socket is not a integer")


def net_close(socket):
   """
   Closes the communication endpoint

   The endpoint is identified by the supplied socket number and deletes it
   for future re-use.
   
   Return Values::
     0  on success.
   On failure, it returns::
    -4 -   when sockfd is not a valid socket descriptor.
    -1 -   on a system call error, with errno containing the error indication.
   """
   if (str(type(socket)) == "<type 'int'>"):
      if socket <= NET_MAX_FD:
         result = net_srv.net_close(socket)
         if result != SUCCESS :
            process_error(result)
      else:
         raise ValueError("socket number exceeds maximum socket number")
   else:
      raise TypeError("socket is not an integer")

def get_peername(socket):
   """
   """
   if str(type(socket)) == "<type 'int'>":
      process_ID = create_string_buffer(4)
      hostname = create_string_buffer(256)
      status = net_srv.net_getpeername(socket,
                                      byref(process_ID),
                                      byref(hostname),
                                      256)
      if status == SUCCESS:
         return hostname.value,ord(process_ID.value)
      else:
         process_error(status)
   else:
      raise TypeError("socket is not a integer")

def get_serverport(end_point):
   """
   """
   if str(type(end_point)) == "<type 'str'>":
      # We only deal with TCP in Net Services
      port = net_srv.net_getservport(end_point,TCP)
      if port != ERROR:
         return port
      else:
         raise Exception("associated port not found")
   else:
      raise TypeError("endpoint is not a string")
