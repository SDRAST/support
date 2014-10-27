import logging

from support.process import invoke

module_logger = logging.getLogger(__name__)

def LAN_hosts_status():
  response = invoke("sudo nmap -sP -PS22 192.168.100.*").stdout.readlines()
  up = []
  down = []
  MAC = {}
  for line in range(4,len(response)-1):
    parts = response[line].strip().split()
    if parts[2] == "report":
      host = parts[4]
      line += 1
      status = response[line].strip().split()[2]
      if status == 'up':
        up.append(host)
        line += 1
        MAC[host] = response[line].strip().split()[2]
      else:
        down.append(host)
    else:
      pass
  return up, down, MAC

if __name__ == "__main__":
  up, down, MAC = LAN_hosts_status()
  print "Up:", up
  print "Down:", down
  print MAC

