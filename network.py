import logging
import socket

from support.process import invoke

module_logger = logging.getLogger(__name__)

def LAN_hosts_status():
  """
  This is too crude; very senstive to format changes
  """
  print "If asked for a password, remember this host is",socket.gethostname()
  response = invoke("sudo nmap -sP -PS22 192.168.100.*").stdout.readlines()
  up = []
  down = []
  IP = {}
  MAC = {}
  ROACHlist = []
  for line in range(4,len(response)-1):
    parts = response[line].strip().split()
    if parts[2] == "report":
      host = parts[4]
      if len(parts) == 6:
        IP[host] = parts[5][1:-1]
      else:
        IP[host] = host
      line += 1
      status = response[line].strip().split()[2]
      if status == 'up':
        up.append(host)
        line += 1
        MAC[host] = response[line].strip().split()[2]
        if MAC[host].split(":")[0] == '02':
          ROACHlist.append(host)
      else:
        down.append(host)
    else:
      pass
  up.sort()
  down.sort()
  ROACHlist.sort()
  return up, down, IP, MAC, ROACHlist
################################ IP support ###################################

def decode_IP(IP_address):
  """
  Returns a long int for an IPv4 or IPv6 address.

  @param IP_address :  like "192.168.1.101"
  @type  IP_address : str of decimal separated ints

  @return: int
  """
  parts = IP_address.split('.')
  if len(parts) == 4 or len(parts) == 6:
    ipvalue = 0
    for i in range(len(parts)):
      shift = 8*(len(parts)-1-i)
      ipvalue += int(parts[i]) << shift
    return ipvalue
  else:
    raise RuntimeError("Invalid IP address: %s" % IP_address)

def decode_MAC(MAC_address):
  """
  Returns a long int for a MAC address

  @param MAC_address : like "00:12:34:56:78:9a"
  @type  MAC_address : str of colon separated hexadecimal ints

  @return: long int
  """
  parts = MAC_address.split(':')
  if len(parts) == 6:
    value = 0
    for i in range(6):
      shift = 8*(5-i)
      value += int(parts[i],16) << shift
    return value
  else:
    raise RuntimeError("Invalid MAC address: %s" % MAC_address)

if __name__ == "__main__":
  up, down, IP, MAC, ROACHlist = LAN_hosts_status()
  print "Up:", up
  print "Down:", down
  print "ROACHes:", ROACHlist
  print "IP:", IP
  print "MAC addresses:", MAC


