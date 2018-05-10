# -*- coding: utf-8 -*-
"""
This implements a Net Services server identified as an EAC.

Because it uses the MySQL database on dsnra it must be tested at JPL

Commands currently implemented on the server::
  AZEL
  AZEL?
  ONSOURCE?
  SOURCE
  STOW
  bye

TO DO::
  * replace calls to Astronomy module with calls to astropy
  * replace current_source_azel with call to astropy
  * replace diag print statements with logging message
"""
import support.NetServices as NS
from support.NetServices.net_IDs import get_net_IDs
import Astronomy as A
import support.text as text
from planetarium2 import current_source_azel 

from select import select
from time import sleep, ctime, time
import re
import numpy as NP
import sys
import thread
import Mysql
import logging
from os.path import splitext

module_logger = logging.getLogger(__name__)
diag = True

class EAC_simulator():
  '''
  Simulates the EAC for DSS-13
  '''
  def __init__(self):
    """
    Initialize EAC simulator for DSS-13

    This will try to get station data from the 'dsn' database.  If that fails,
    the data are obtained from a local file.  It also initializes the lists
    of ports to be monitored.by the EAC and opens the log.
    """
    try:
      self.db_connection = Mysql.open_db('dsn',
                                         'dsnra.jpl.nasa.gov',
                                         'kuiper',
                                         'dsnra')
    except Exception:
      self.db_connection = None
    if self.db_connection:
      answer = Mysql.ask_db(self.db_connection,
                            "select * from dsn.source_name;")
      if diag:
        print "Known sources:\n",answer
    else:
      if diag:
        print("MySQL database could not be accessed; using local files")
      self.catalogs = A.show_catalogs()

    net_srvr, net_task = get_net_IDs()
    self.server_name = net_srvr['ANT_SRV1']
    if diag:
      print "My name is",self.server_name
    try:
      self.listen_fd = NS.net_init(self.server_name)
    except SystemError, details:
      print "net_init failed:",details
    else:
      self.read_fds = [self.listen_fd]
      self.write_fds = []
      self.exception_fds = []
      self.active_threads = []

      self.az = 180.0; self.el = 89.5
      self.onsource = True

      self.log = open("EAC.log","w+")
      self.run()

  def run(self):
    self.running = True
    while self.running:
      self.log.flush()
      # Check to see if any sockets need service
      try:
        pending_read,pending_write,pending_exception = \
          select(self.read_fds, self.write_fds, self.exception_fds, 1)
      except KeyboardInterrupt:
        self.running = False
      if len(pending_read):
        if diag:
          print "There are pending sockets for reading"
        for fd in pending_read:
          if fd == self.listen_fd:
            if diag:
              print "new client"
            client_fd = NS.net_accept(self.listen_fd,NS.BLOCKING)
            if client_fd > 0:
              self.log.write("new client connected at fd "+str(client_fd)+"\n")
              self.read_fds.append(client_fd)
              if diag:
                print "read_fds is now",self.read_fds
            else:
              print "Invalid client fd"
          else:
            # Existing client requests service
            # start a new thread to handle the request
            self.active_threads.append(thread.start_new(self.handleRequest,
                                                        (fd,)))

  def handleRequest(self,client_fd):
    """
    Process request

    in spawned thread and reply
    """
    try:
      nchars,message = NS.net_recv(client_fd,NS.BLOCKING)
    except Exception,details:
      print "net_recv failed:",details
      nchars = 0
    if nchars:
      if diag:
        print "Read socket",client_fd,':',message
      reply = self.process_request(client_fd,message)
      if diag:
        print "Reply is:",reply
    else:
      # client went away
      try:
        self.read_fds.remove(client_fd)
      except Exception, details:
        print "Could not remove absent client file descriptor"
        print details
      reply = ""
    if reply != "":
      self.send_response(client_fd,reply)
    # task finished
    thread.exit()
    # Ad hoc fix to keep EAC simulator from running away when exp_control
    # disconnects
    if reply == "":
      self.running = False

  def process_request(self,client_fd,message):
    """
    Process a client request

    @type  client_fd : socket descriptor
    @param client_fd : socket of the client task sending the request

    @type message  : str
    @param message : request
    """
    if diag:
      print "Received:",message
    self.log.write(ctime(time()) + ": received: "+message+"\n")
    parsed = message.split()
    if parsed[0].upper() == "SOURCE":
      # There are various versions of this command to handle
      return self.parse_source(client_fd, parsed)
    elif parsed[0].upper()[:8] == "ONSOURCE":
      if self.onsource:
        return "Tracking"
      else:
        return "Slewing"
    elif parsed[0].upper() == "AZEL":
      if len(parsed) == 3:
        new_az = parsed[1]
        new_el = parsed[2]
        chars_sent = NS.net_send(client_fd,"azel: completed",NS.BLOCKING)
        self.move_antenna(float(new_az),float(new_el),client_fd)
        return "Onpoint"
      else:
        return "azel: rejected. Wrong no. of args"
    elif parsed[0].upper() == "AZEL?":
      return "azel: %7.3f  %7.3f" % (self.az, self.el)
    elif parsed[0].upper() == "STOW":
      self.move_antenna(180.,89.5,client_fd)
      return "Stowed"
    else:
      return "OK"

  def send_response(self,fd,reply):
    chars_sent = NS.net_send(fd,reply,NS.BLOCKING)
    self.log.write("Reply: "+reply+"\n")
    if diag:
      print "Replied:",reply
      print chars_sent,"characters sent"

  def move_antenna(self,new_az,new_el,client_fd):
    """
    Move the antenna to a designated azimuth and altitude.

    Note
    ====
    When slewing to a source with changing azimuth and altitude,
    the current source ra and dec should really be used to determine
    the final location.
    """
    self.onsource = False
    delta_az = new_az - self.az
    delta_el = new_el - self.el
    # which is the larger move?
    if abs(delta_az) > abs(delta_el):
      max_az_step = 0.2
      num_az_step = abs(delta_az)/max_az_step
      max_el_step = abs(delta_el)/num_az_step
    elif abs(delta_az) < abs(delta_el):
      max_el_step = 0.2
      num_el_step = abs(delta_el)/max_el_step
      max_az_step = abs(delta_az)/num_el_step
    else:
      max_az_step = max_el_step = 0.2
    while abs(delta_az) > 0.01 or abs(delta_el) > 0.01:
      delta_az = new_az - self.az
      # The antenna moves at 0.2 deg/sec
      if abs(delta_az) > 0.4:
        # high speed speed
        az_step = maz_az_step
      elif abs(delta_az) > 0.1:
        # medium speed slew
        az_step = 0.02
      elif abs(delta_az) > 0.01:
        # slow
        az_step = 0.002
      elif abs(delta_az) < 0.003:
        # we're there
        az_step = 0.0
      if delta_az < 0: # negative azimuth move
        self.az -= az_step
      else:            # positive azimuth move
        self.az += az_step

      # Let's assume the same elevation speed
      delta_el = new_el - self.el
      if abs(delta_el) > 0.4:
        # high speed
        el_step = max_el_step
      elif abs(delta_el) > 0.1:
        # intermediate speed
        el_step = 0.02
      elif abs(delta_el) > 0.01:
        # slow speed
        el_step = 0.002
      elif abs(delta_el) < 0.003:
        # high speed slew
        el_step = 0.0
      if delta_el < 0:
        self.el -= el_step
      else:
        self.el += el_step
      message = "azel: %7.3f  %7.3f" % (self.az, self.el)
      self.send_response(client_fd, message)
      sleep(1)
    self.onsource = True

  def parse_source(self,client_fd,parsed):
    """
    Process EAC SOURCE command
    """
    name = parsed[1]
    if len(parsed) == 2:
      # The message consists of SOURCE and a source name
      try:
        ra50, dec50, Vlsr = self.find_source(self.catalogs,name)
        print name, ra50, dec50
        valid_input = True
      except TypeError:
        return "source: rejected. Invalid command."
    elif len(parsed) == 4:
      # The message has the form SOURCE  NAME  HH.HH  DD.DD
      ra50 = float(parsed[2])
      dec50 = float(parsed[3])
      valid_input = True
    elif len(parsed) == 5:
      # The message includes a specific epoch
      ra50 = float(parsed[2])
      dec50 = float(parsed[3])
      epoch = parsed[4]
      # Needs code to convert epoch to 1950.
      valid_input = True
    else:
      return "source: rejected. Invalid command."
    if valid_input:
      # Compute the new azimuth and elevation
      new_az,new_el = current_source_azel(ra50,dec50)
      self.send_response(client_fd,"source: completed")
      self.move_antenna(new_az,new_el,client_fd)
      # Now that we are close enough, send the command to the EAC
      self.send_response(client_fd, ' '.join([name,str(ra50),str(dec50)]))
      return "Onpoint"

  def find_source(self,catalogs,src_name):
    found = False
    for cat in catalogs:
      sources = A.get_sources(splitext(cat)[0])
      for src in sources:
        if text.nocase_distance(src_name,src) < 2:
          if diag:
            print "Found:",cat, src_name, src, sources[src]
          found = True
          break
    if found:
      return sources[src]
    else:
      return None

if __name__ == "__main__":

  logging.basicConfig(level=logging.DEBUG)
  mylogger = logging.getLogger()

  fake_EAC = EAC_simulator()
