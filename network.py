import logging
import socket

from support.process import invoke

module_logger = logging.getLogger(__name__)

def LAN_hosts_status():
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

if __name__ == "__main__":
  up, down, IP, MAC, ROACHlist = LAN_hosts_status()
  print "Up:", up
  print "Down:", down
  print "ROACHes:", ROACHlist
  print "IP:", IP
  print "MAC addresses:", MAC


