"This is the world we live in... relying on each other's mistakes. To manipulate one another. Use one another..."


__________________________

This exploit allows the attacker a reverse shell on the target within the local network. This exploit should run on both Windows and Linux machines, both client and server. An executable can be created out of the client_reverse_shell script, and embedded into a file. But if you want to exploit a windows device, you'll need to run pyinstaller on a windows device/VM. Vice-versa for a linux target:

pyinstaller --onefile --noconsole client_reverse_shell2.py
The executable should then be in a 'dist' folder. 

1. Force the target machine to ping sweep the local network for all Live ip adresses in the network. The pings are limited to 1 for each address, and done concurrently for a quicker and more efficient way of obtaining all the addresses. The time limit on the response is set at 1sec to give the target machine enough time send and recieve ICMP packets.

2. Once all the live ips have been gathered, force the client to scan each live ip for an open port: the port that my tcp server will be listening on. 

3. Once a connection has been established, we can implement a backdoor by copying ourselves into the root directory. We change the registry keys on the target machine so that we have persistence. 

