"""At a deeper level, Net Services has a specific message structure with
a header.  This can be used to validate the messages themselves.

A Net Services message consists of a data structure 'msg_hdr' and
message text.  The header consists of:
U32 - message ID, consisting of
      U16 - server system ID
            1 - EAC
            2 - PCFS
            3 - RAC
            4 - RMON, remote monitor
            5 - RCTL, remote controller
            6 - SPEC, spectrometer
            7 - SRVR, unspecified but acceptable server
      U8  - message size code: the message size is 128 * (size_code+1).
            Thus the default message size is 128 bytes and the maximum
            is 32768.
      U8  - message type
            1 - CMD
            2 - RSP
U32 - source ID, the ID of the originator, called 'my_process_id' in this
      code. 'my_process_ID' is an integer but for convenience is specified
      as a symbolic name which can be obtained with 'get_net_IDs()' from
      module 'net_IDs'.
"""
from struct import *
from socket import htonl, htons

system_ID = {
   'EAC':1, 'PCFS':2, 'RAC':3, 'RMON':4, 'RCTL':5, 'SPEC':6, 'SRVR':7
}
msg_type = {
   'CMD':1, 'RSP':2, 'ANT_ASG':3, 'LINK_UNASG':4, 'EVENT':5, 'MON_DATA':6
}

def decode(message):
   system_ID,sizecode,msg_type,source_ID = unpack('hcci',message[0:8])
   msg = message[8:]
   return htons(server_ID), \
          sizecode, \
          msg_type, \
          htonl(source_ID), \
          msg

def encode(system, message_type, message, my_ID):
   sizecode = len(message)/128 + 1
   header = pack('hbbi',
                 htons(system_ID[system]),
                 sizecode,
                 msg_type[message_type],
                 htonl(my_ID) )
   return header+message
