# -*- coding: utf-8 -*-
"""
module tunneling - set up tunnels and mount remote file systems

This uses the new tunneling scripts, which date from Sep.2012.

Tunneling
=========
Tunnel parameters are predefined and can be obtained with show_remote_names().
The domain and host names are nicknames for easy remembering.  They are
accessed as 'localhost:port'.  A tunnel is set up with:

In [1]: from tunneling import *

In [2]: t = Tunnel("ra")

It uses the script 'ssh-tunnel2' which will use the local username or, for
some hosts, known alternates like 'ops'.

Remote Mounting
===============
Once a tunnel is established, remote file systems can be mounted through it
like this:

In [3]: m = RemoteDir("ra","/home/kuiper")

To see where it is mounted locally:

In [4]: m.mountroot
Out[4]: '/home/kuiper/mnt'

In [5]: m.mountpoint
Out[5]: 'ra'

The default local mount point base is $HOME/mnt.  The mount points are
usually temporary directories named with the remote host name though a
specific mountpoint can be specified in "$HOME/.mntrc".

If you attempt to mount a remote directory without the required tunnel,
a tunnel will be created.

Pushing Keys
============
To avoid having to give a password for ssh logins which use simple passwords,
one can push keys to the remote host which will authenticate you in future.
This does not work across a gateway requiring two-factor (SecurID)
authentication.

There is a Catch 22 situation for now:  If the keys have not be pushed on to
the remote host then it will want a password and the interactive mechanism for
doing that has not been installed.  Check paramiko examples for hints.

Port Proxies
============
After a tunnel exists, it can be used to create local proxies for ports
on the remote host:

In [6]: T.makePortProxy('dsnra',12345,'dsnra',80)

Now if a browser is pointed at localhost:12345 it will get a response from
dsnra:80.

Notes
=====
The remote mount class came from:
http://code.activestate.com/recipes/573473-sshfs-mount-tool/

For notes on socket programming see:
http://dsnra.jpl.nasa.gov/software/sockets/ http://dsnra.jpl.nasa.gov/software/Python/html/lib/module-socket.html

For notes on tunneling see:
/home/kuiper/Projects/SPIE/SPIE-2012/ssh-tunnels.html
"""
import getopt
import os
import posix
import getpass
from   subprocess import PIPE, Popen
import sys
import shlex
import signal
import re
import time
import random
import select
import logging

import support
from   support.process import invoke, search_response
from   support.network import get_domain

module_logger = logging.getLogger(__name__)

DEFAULTMOUNTROOT= os.environ.get ("HOME") + os.sep + "mnt"

# --------------------------- module classes ------------------------------

class TunnelingException(Exception):
  """
  Handle tunnuling module exceptions.

  Note
  ====
  All in-line error messages need to be replaced with this.
  """
  def __init__(self, text):
    """
    Define the error message

    @param text : message to be displayed
    @type  text : str

    @return: None
    """
    self.text = text
  
  def __str__(self):
    """
    Display the error text
    
    @return: error text
    """
    return repr(self.text)

class RemoteDir:
  """
  Class for locally mounting file systems.

  Public methods:
  usage(short=True)                             - help text
  do_mount(Tunnel instance, remote mount point) - mount the remote filesystem
  do_umount_all()                               -
  do_umount(mountpoint)                         -
  main_loop()                                        - user interface
  """
  def __init__(self, endpoint, remoteMP="/"):
    """
    Create an instance of a remote file system mounted locally.

    To see the argument list do 'RemoteDir.usage()'

    @param endpoint : name of the tunnel endpoint.
    @type  endpoint : str

    @param remoteMP : point of remote filesystem to be mounted
    @type  remoteMP : str

    @return: RemoteDir() instance
    """
    self.logger = logging.getLogger(module_logger.name+".Tunnel")
    self.read_mountroot_cfg ()
    if not os.path.exists (self.mountroot):
      os.mkdir (self.mountroot)
      self.logger.debug(" Creating mountroot in %s",self.mountroot)
    self.host = endpoint
    self.uid = os.getuid()
    self.mountpoint=None
    self.mp=None
    try:
      self.port=PORT[endpoint]
    except IndexError, details:
      raise IndexError, details
    except Exception, details:
      raise Exception, details
    existing_tunnels = check_for_tunnels()
    self.logger.debug(" existing tunnels: %s",str(existing_tunnels))
    # get or create the appropriate tunnel instance
    self.tunnel = Tunnel(endpoint)
    success = self.do_mount (self.tunnel, remoteMP=remoteMP)

  def usage(self, short=True):
    """
    RemoteDir() class usage

    @param short : abbreviated version if True (default)
    @type  short : boolean

    @return: None
    """
    if short:
      print """%s [-u mountpoint] [-p port] [-m mountpoint] <-a|-l|-h|user@host:path>""" \
            % sys.name
    else:
      print """%s [OPTIONS] SOURCE
        OPTIONS
        -a                            Unmount all sshfs-mounts
        -u <mountpoint>               Unmount mount
        -p <port>                     Use specified port
        -m <mountpoint>               Don't select mountpoint automatically
        -l                            List all mounts
        -h                            This help page

        SOURCE is any ssh address. RemoteDir will use the current user if no username
        is given. If the path is omitted RemoteDir will mount the home directory.
        Mountpoint is always without directories, see .mntrc

        EXAMPLES (using ipython)
        [1] run tunneling.py kuiper@ra
        [2] run tunneling.py kuiper@dsnra:/home
        [3] run tunneling.py -m my_mount_point kuiper@roachnest:/
        [4] run tunneling.py -p 50091 kuiper@localhost
        [5] run tunneling.py -u my_mount_point
        [6] run tunneling.py -a
        """ % sys.name

  def _get_mounted_fs (self):
    """
    reads mtab and returns a list of mounted sshfs filesystems.

    Example:
    [[source, mountpoint, filesystem, options, p1, p2],...] = _get_mounted_fs()

    @return: list of mount points for remote file systems
    """
    try:
      lines = [line.strip("\n").split(" ")
                 for line in open ("/etc/mtab", "r").readlines()]
      return [mount for mount in lines if mount[2]=="fuse.sshfs"]
    except:
      print self.name,": Could not read mtab"

  def read_mountroot_cfg(self):
    """
    Read the users .mntrc file or create one if it doesn't exist

    At the moment, the only useful entry in the file is something like:
    mountroot=/home/user/mnt.  A user could specify another root mount
    point, say one for a project.

    @return: None
    """
    rcfile = os.environ.get ("HOME") + os.sep + ".mntrc"
    if os.path.exists (rcfile):
      try:
        for line in open (rcfile, "r").readlines():
          if line.startswith ('mountroot='):
            self.mountroot = line.rsplit ("=")[1].strip("\n")
      except:
        print self.name,": Configuration file exists but is not readable."
    else:
      try:
        self.mountroot = DEFAULTMOUNTROOT
        open (rcfile, "w").writelines ("mountroot=%s" % DEFAULTMOUNTROOT)
        print self.name,": Writing default mountroot %s to .mntrc" % DEFAULTMOUNTROOT
      except:
        print self.name,": Could not write .mntrc (%s)" % rcfile

  def _split_ssh_source (self,source):
    """
    split the values of a ssh source, guess the missing parts of
    user@host:path

    Example:
    (user, host, path) = _split_ssh_source("user@host:path")

    @param source : "user@host:path" for sshfs
    @type  source : str

    @return: (user, host, path)
    """
    try:
      user,hostpart = source.split("@")
    except ValueError:
      user = getpass.getuser()
      try:
        host, path = source.split(":")
      except:
        path = "."
        host = source
    else:
      try:
        host, path = hostpart.split(":")
      except:
        path = "."
        host = hostpart
    return (user, host, path)

  def _get_possible_mountpoint (self):
    """
    guesses a possible free mountpoint and returns it.

    Example:
    _get_possible_mountpoint (user, host) -> mountpoint

    @return: local mount point
    """
    if not self.mountpoint:
      self.mountpoint = self.host
    mp = self.mountroot + os.path.sep + self.mountpoint
    return mp

  def do_mount (self, tunnel, remoteMP="/"):
    """
    mount ssh source as local filesystem by calling sshfs

    Example:
    do_mount(mytunnel, "/home/me")

    @param tunnel : ssh tunnel to a remote host
    @type  tunnel : Tunnel() instance

    @return: True on success
    """
    self.user = tunnel.user
    self.port = tunnel.port
    self.path = remoteMP
    self.mp = self._get_possible_mountpoint()
    if not os.path.exists (self.mp):
      self.logger.debug(
        "do_mount: Creating mountpoint *s",str(self.mp))
      os.mkdir (self.mp)
    sshfs = "%s@localhost:%s" % (self.user, self.path)
    # already mounted?
    response = search_response(['mount'],['grep',sshfs])
    if response:
      self.logger.debug(
        "do_mount: already mounted:\n%s",str(response))
      self.mp = response[0].strip().split()[2]
      self.mountpoint = os.path.basename(self.mp)
      self.mountroot = os.path.dirname(self.mp)
      status = 0
    else:
      command = 'sshfs -p %d -o uid=%d -o cache=no "%s" "%s"' % (self.port,
                                                                 self.uid,
                                                                 sshfs,
                                                                 self.mp)
      self.logger.debug("do_mount: login: %s",sshfs)
      self.logger.debug("do_mount: mount command:\n%s",command)
      status = os.system (command)
    if status == 0:
      self.logger.debug("do_mount: %s: %s mounted as %s in %s",
                           self.host, self.path, self.mountpoint,
                           self.mountroot)
      return True
    else:
      self.logger.warning("do_mount: Mount failed")
      try:
        os.rmdir(self.mp)
      except OSError, details:
        self.logger.error("do_mount: could not remove",self.mp,exc_info=True)
      return False

  def do_umount_all(self):
    """
    Unmounts all sshfs filesystems

    @return: None
    """
    for source,mountpoint,fstype,opts,p1,p2 in self._get_mounted_fs():
      self.do_umount (mountpoint.rsplit (os.path.sep)[-1])

  def do_umount (self, mountpoint):
    """
    Unmounts and removes a specific sshfs filesystem

    @param mountpoint : local mountpoint relative to self.mountroot
    @type  mountpoint : str

    @return: None
    """
    if os.path.exists (self.mountroot + os.path.sep + mountpoint):
      os.system ("fusermount -u " + self.mountroot + os.path.sep + mountpoint)
      os.rmdir (self.mountroot + os.path.sep + mountpoint)
      self.logger.info("do_umount: %s unmounted", str(mountpoint))

  def main_loop(self):
    """
    This processes the command line arguments when this module
    is run as a script.

    @return: None
    """
    try:
      opts, args = getopt.getopt(self.argv,
                                 "au:lr:m:h",
                  ["all", "unmount", "list", "remote", "mountpoint", "help"])
    except getopt.GetoptError:
      self.usage()
      sys.exit (2)

    for opt, arg in opts:
      if opt in ("-u", "--umount"):
        self.do_umount(arg)
        return 0
      elif opt in ("-l", "--list"):
        do_list()
        return 0
      elif opt in ("-h", "--help"):
        self.usage(short=False)
        return 0
      elif opt in ("-a", "--all"):
        self.do_umount_all()
        return 0
      elif opt in ("-r", "--remote_host"):
        self.endpoint=int(arg)
      elif opt in ("-m", "--mountpoint"):
        self.mountpoint=arg
    # args is everything that follows the last option
    self.tunnel = Tunnel(self.endpoint)
    self.do_mount(t,remoteMP=self.mountpoint)

class Tunnel:
  """
  Class to create an ssh tunnel object to a remote host.

  Public methods:
  close() - destroy the tunnel
  
  Public attributes:
  port   - port on the local host assigned to the tunnel
  user   - username on the remote host
  host   - informal name of the remote host
  pid    - process ID of the tunnel session
  """
  def __init__(self,host):
    """
    Create a Tunnel() instance.

    If a tunnel already exists to the designated host, then
    then this just creates a tunnel object to describe it.  If it does
    not exist, it creates the tunnel.

    Notes
    =====

    If a pre-existing tunnel is used then it is possible that the remote
    username is not the owner of the present task.  This might be
    intentional, such as if the remote user is 'ops', or it might be
    a real conflict.  The script needs to replace the user name 'unknown'
    with an appropriate name.

    @param host : host nickname as defined in ssh-tunnel script
    @type  host : str

    @return: Tunnel() instance
    """
    self.logger = logging.getLogger(module_logger.name+".Tunnel")
    self.logger.debug(" checking for tunnel to %s", host)
    response = self.check_for_tunnel(host)
    if response == 0:
      self.logger.debug(" no tunnel found; create a new one")
      # make a tunnel
      command = '/usr/local/scripts/ssh-tunnel "%s"' % (host)
      self.logger.debug(" doing: %s",command)
      self.p = invoke(command)
      response = self.p.stdout.readline()
      self.logger.debug(" got: %s",response)
      parts = response.split()
      if parts[-2] == "recognized":
        # not recognized
        raise TunnelingException(response.strip())
      else:
        self.port = int(parts[-1])
        self.user = parts[2]
        self.host = parts[4]
        time_left = 30. #seconds
        while self.check_for_tunnel(self.host) == 0 and time_left > 0.:
          time.sleep(0.5)
          time_left -= 0.5
          print "%6.1f\r" % time_left,
        self.p.stdout.close()
        self.p.stderr.close()
        if time_left <= 0.:
          # timed out
          self.port = 0
          raise TunnelingException(" timed out")
        else:
          self.logger.debug(" opened tunnel to %s",self.host)
    else:
      # a tunnel exists
      self.logger.debug(" tunnel exists")
      self.port = int(response)
      self.host = host
      if host == "mmfranco-0571605":
        # This is also REALLY UGLY
        self.user = 'pi'
      else:
        self.user = "unknown"
    self.pid = self._get_child()
    if self.user == "unknown":
      self.get_user()
    self.logger.debug(" tunnel has PID %d at %d for %s",
                      self.pid, self.port, self.user)
    
  def get_user(self):
    """
    Get the owner of the tunnel

    @return: owner
    """
    self.user = 'unknown'
    output = search_response(["ps", "-ef"],["grep", str(self.pid)])
    for line in output:
      parts = line.strip().split()
      if int(parts[1]) == self.pid:
        self.user = parts[0]
        break
    return self.user

  def __repr__(self):
    """
    How the tunnel instance reports itself.

    @return: str
    """
    return "Tunnel instance: localhost:" + str(self.port) + " is equivalent to " \
           + self.user + "@" + self.host

  def check_for_tunnel(self,host):
    """
    See if there is a tunnel to the designated host

    The domain name and host name are defined in tunnel_ports

    @param host : nickname for remote host
    @type  host : str

    @return: port number, or 0 if there is no tunnel
    """
    self.logger.debug("check_for_tunnel: invoked")
    tunnels = check_for_tunnels()
    if tunnels.has_key(host):
      return int(tunnels[host])
    elif tunnels.has_key('wbdc') and host == "mmfranco-0571605":
      # This is REALLY UGLY
      return int(tunnels['wbdc'])
    else:
      return 0
  
  def _get_child(self):
    """
    Gets the PID of the process sustaining the tunnel

    @return: int
    """
    output = search_response(["ps", "-ef"],["grep", "xterm"])
    #p1 = Popen(["ps", "-ef"], stdout=PIPE)
    #p2 = Popen(["grep", "xterm"],  stdin=p1.stdout, stdout=PIPE)
    #waiting = True
    #while waiting:
    #  try:
    #    output = p2.stdout.read()
    #    waiting = False
    #  except IOError:
    #    # probably an interrupted system call.  Try again
    #    continue
    module_logger.debug("_get_child: search_response gave\n%s",output)
    parts = output[0].split()
    pid = parts[1]
    user = parts[0]
    if pid.isdigit():
      return int(pid)
    else:
      return None

  def push_keys(self):
    """
    Install ssh keys on remote host

    This appends the key strings as text to the remote authorized_keys file.

    Note:
    =====
    The permissions for .ssh/authorized_keys should be -rw-r----- (0640).
    The permissions for .ssh should be -rwx------ (0700).
    """
    ssh_rsa_fd = open(os.environ.get ("HOME") + os.sep
                      + ".ssh" +os.sep + "id_rsa.pub","r")
    ssh_dsa_fd = open(os.environ.get ("HOME") + os.sep
                      + ".ssh" +os.sep + "id_dsa.pub","r")
    rsa_key = ssh_rsa_fd.read()
    dsa_key = ssh_dsa_fd.read()
    ssh_rsa_fd.close()
    ssh_dsa_fd.close()

    remote_file = ".ssh/authorized_keys"
    push_command1 = "echo "+rsa_key+" >> "+remote_file
    try:
      self.remote_command(push_command1)
    except Exception, details:
      raise TunnelingException("push_keys() remote_command() 1 failed:\n"
                               + str(details))
      return False
    push_command2 = "echo "+dsa_key+" >> "+remote_file
    try:
      self.remote_command(push_command2)
    except Exception, details:
      raise TunnelingException("push_keys() remote_command() 2 failed:\n"
                               + str(details))

  def remote_command(self,cmd):
    """
    Send a command to be executed on the remote host

    This is for commands end immediately, like "ls" or "date".

    @param cmd : command to be executed
    @type  cmd : str

    @return: response from task on remote host
    """
    command_line = "ssh "+"-p "+str(self.port)+" "+self.user+"@localhost "+cmd
    p = invoke(command_line)
    err = p.stderr.read()
    if err != "":
      print "Error:",err,"\nResult:"
    response = p.stdout.read()
    del p
    return response
  
  def close(self):
    """
    Kills the process which supports the tunnel.

    @return: True on success
    """
    if self.pid:
      os.kill(self.pid, signal.SIGKILL)
      return True
    else:
      return False

# ------------------------ module methods -------------------------------

def free_socket():
  """
  Return a free socket
  """
  found = 1
  while found:
    trial = random.randrange(1024,65535)
    found = search_response(['netstat','-vatn'],['grep',str(trial)])
  return trial

def makePortProxy(endpoint,
                  localport,
                  remotehost,
                  remoteport,
                  user=None):
  """
  Connect a local port to a port on a remote host through a tunnel

  This uses an existing tunnel to create another tunnel through it so that
  a port on a remote host can be accessed via a local port.

  One advantage is that only one tunnel needs to be created through a firewall
  that requires active authentication.  Another is when the remote port is
  a privileged port, like 80 (web server) or 5900 (X11 console).

  @param endpoint : endpoint of the existing tunnel (through the firewall)
  @type  endpoint : str

  @param localport : port number on localhost to serve as proxy
  @type  localport : int

  @param remotehost : host with the port to be accessed
  @type  remotehost : int

  @param remoteport : port on the remote host
  @type  remoteport : int

  @param user : remote host user name, default is local user name
  @type  user : str
  """
  tunnel_port = PORT[endpoint]
  module_logger.debug('makePortProxy: called for port %d', tunnel_port)
  if tunnel_port == 50099:
    # more REALLY UGLY <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    user = 'pi'
  if user == None:
    user=support.get_user()
  module_logger.debug('makePortProxy: user is %s', user)
  command_list = ["ssh", "-N", "-p", str(tunnel_port),
                  "-L",str(localport)+":"+remotehost+":"+str(remoteport),
                  user+"@127.0.0.1", "&"]
  module_logger.debug("makePortProxy: command is\n%s",str(command_list))
  p = invoke(command_list)
  return p

def get_remote_names():
  """
  Identifies tunnel port numbers.by site and host.

  @return: a dictionary of the form {port: [site, host], ...}.
  """
  name_data = {}
  for (host,port) in PORT.items():
    name_data[port] = host
  return name_data

def make_port_dict():
  """
  Makes dictionaries of the remote host data.

  GATEWAY is of the form {remote_host: gateway_host, ...}.
  IP is of the form {remote_host: remote_host_IP_address, ...}.
  PORT is of the form {remote_host: tunnel_port_on_localhost, ...}.

  @return: (GATEWAY, IP, PORT)
  """
  GATEWAY = {}
  IP = {}
  PORT = {}
  module_logger.debug("make_port_dict: opening tunnel_ports")
  fd = open("/usr/local/scripts/tunnel_ports","r")
  module_logger.debug("make_port_dict: opened tunnel_ports")
  text = fd.readlines()
  fd.close()
  for line in text:
    if line[:7] == "declare":
      continue
    module_logger.debug("make_port_dict: processing: %s", line)
    if len(line.strip()):
      exec(line.strip())
  return GATEWAY, IP, PORT

def check_for_tunnels():
  """
  Checks to see which tunnels are open

  Note
  ====
  We define ports in the range 50010-50100.  There's a 1% chance that the
  system has assigned a port in that range.  The code checks that a port
  matches a site/host definition.  There's still a chance that the system
  has assigned a port which has been defined for tunnel use.  The code does
  not yet check if the port, if it matches a site/host, is actually a tunnel.

  return: dict as for make_port_dict()
  """
  # Get a list of current sockets
  p = invoke("netstat -vat")
  try:
    err = p.stderr.read()
  except IOError:
    module_logger.debug("check_for_tunnels: Could not read stderr",
                        exc_info=True)
  else:
    if err.isspace() == False:
      module_logger.info("check_for_tunnels: %s",err)
  response = p.stdout.read().split("\n")
  #module_logger.debug("netstat -vat response:\n%s",response)
  tunnels = {}
  name_data = get_remote_names()
  for line in response:
    parts = line.split()
    if parts and parts[0] == 'tcp':
      local,remote,status = parts[3:]
      host,port = local.split(":")
      if port.isdigit():
        if int(port) > 50010 and int(port) < 50100:
          try:
            remote_host = name_data[int(port)]
          except KeyError, details:
            # Sometimes the OS uses a port in this range
            print "check_for_tunnels: active port",details,"not defined"
            break
          else:
            tunnels[remote_host] = int(port)
  module_logger.debug("check_for_tunnels: found %s",str(tunnels))
  return tunnels

def need_tunnel(server):
  """
  Reports whether a tunnel is needed to connect to the server.

  This needs to be able to handle fully qualified host names and IP addresses

  @param server : fully qualified server name or IP address
  """
  output = search_response(['ip', 'route', 'show'],['grep', 'default'])
  gateway = output[0].strip().split()[2]
  # This will fail if the gateway is ever not a single digit.
  local_domain = get_domain(gateway[:-2])

  parts = server.split('.')
  if parts[-1].isalpha():
    if re.search("fltops", server):
      remote_domain = "fltops"
    elif re.search("jpl", server):
      remote_domain = "jpl"
    else:
      remote_domain = "other"
  elif parts[0].isdigit():
    remote_domain = get_domain('.'.join(parts[:-1]))
    
  module_logger.debug("need_tunnel: local domain is %s, remote domain is %s",
                      local_domain, remote_domain)
  if remote_domain == "fltops" and local_domain != "fltops":
    need = True
  elif remote_domain == "jpl" and local_domain == "other":
    need = True
  else:
    need = False
  return need

def do_list():
  """
  List all the sshfs-mounted filesystems

  @return: None
  """
  for src,mp,fs,opts,p1,p2 in self._get_mounted_fs():
    print "%25s mounted on %s" % (src,mp)

GATEWAY, IP, PORT = make_port_dict()

# ------------- provides a program for tunnel management ------------

if __name__ == '__main__':
  """
  This is invoked if the script is run as a program.

  Example:
    run tunneling.py -p 50091 kuiper@localhost
  The file system attributes can be queried:
  
  In [1]: run tunneling.py -p 50091 kuiper@localhost
  kuiper@localhost:. mounted as kuiper-localhost:50091 in /home/kuiper/mnt

  In [2]: m.mountpoint
  Out[2]: 'kuiper-localhost:50091'

  In [3]: m.mountroot
  Out[3]: '/home/kuiper/mnt'

  In [4]: m.port
  Out[4]: 50091

  In [5]: m.name
  Out[5]: 'mnt'

  In [6]: m.uid
  Out[6]: 101513
  """
  if len(sys.argv) == 1:
    RemoteDir("").usage(short=False)
  else:
    m = RemoteDir("mnt")
    m.argv = sys.argv[1:]
    m.main_loop()

