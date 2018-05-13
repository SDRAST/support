import logging
import socket

from support.process import invoke

module_logger = logging.getLogger(__name__)

# I need to get a definitive list for each domain
networks = {"fltops": ["137.228.202",
                       "137.228.203",
                       "137.228.207",
                       "137.228.236",
                       "137.228.246",
                       "137.228.247"],
           "jpl": ["128.149.22",
                   "128.149.252",
                   "137.79.89"]}

services = {"rdp": 3389, "vnc": 5900, "vncJava": 5800, "ssh": 22, "MSrcp": 135,
            "ftp": 21, "sftp": 115}

def LAN_hosts_status(port=22, private=False):
  """
  Get information about and status of local network hosts with port open
  
  Returns a dict with::
    - "up":    hosts up
    - "down":  hosts down
    - "IP":    IP addresses
    - "MAC":   MAC addresses
    - "ROACH": list of ROACHes
  
  This is too crude; very senstive to format changes
  """
  print "If asked for a password, remember this host is",socket.gethostname()
  domain = get_local_network(private=private)
  response = invoke("sudo nmap -sP -PS"+str(port)+" "+domain+".*").stdout.readlines()
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
  return {"up": up,
          "down": down,
          "IP": IP, 
          "MAC:": MAC,
          "ROACH": ROACHlist}

def get_local_network(private=False, subnet=100):
  """
  Returns the IP address of the local network
  
  Defaults to the local area network.  If 'private", defaults to '100' for
  the ROACH network.
  """
  if private:
    IP = socket.gethostbyname("192.168."+str(subnet)+".1")
  else:
    IP = socket.gethostbyname(socket.gethostname())
  return '.'.join(IP.split('.')[:-1])

def get_domain(netIP):
  """
  Returns the networks key whose list contains netIP
  """
  domain = ""
  for key in networks.keys():
    for IP in networks[key]:
      if IP == netIP:
        domain = key
        break
  if domain == "":
    domain = "other"
  return domain

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


