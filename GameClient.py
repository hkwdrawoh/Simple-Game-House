#!/usr/bin/python3

import socket
import sys

def main(argv):
	# create socket and connect to server
	try:
		sockfd = socket.socket()
		sockfd.connect((argv[1], int(argv[2])))
	except socket.error as emsg:
		print("Error: (Client socket) ", emsg)
		sys.exit(1)

	# try login
	login_suc = False
	while not login_suc:
		# send login credentials to server
		print("Please input your user name:")
		username = input()
		print("Please input your password: ")
		password = input()
		loginmsg = f"/login {username} {password}"
		sockfd.send(loginmsg.encode('ascii'))

		# receive login status
		statuscode = recvmsg(sockfd)
		login_suc = True if statuscode == "1001" else False

	# in game hall
	while True:
		# send msg
		try:
			clientmsg = input()
			sockfd.send(clientmsg.encode('ascii'))
		except socket.error as err:
			print("Error: (Send msg) ", err)
			sys.exit(1)

		# recv msg
		statuscode = recvmsg(sockfd)

		# decode msg for 4001 and 3011
		if statuscode == "4001":
			break
		if statuscode == "3011":
			while statuscode != "3012":
				statuscode = recvmsg(sockfd)
		
	# close connection
	print("Client ends")
	sockfd.close()

def recvmsg(sockfd):
	# recv msg
	try:
		statusmsg = sockfd.recv(1024)
	except socket.error as err:
		print("Error: (Recv msg) ", err)
		sys.exit(1)

	# decode msg
	try:
		if statusmsg:
			statusmsg = statusmsg.decode()
			statuscode, statusdes = statusmsg.split(" ", 1)
			print(statuscode, statusdes)
			return statuscode
	except:
		return "4002"

# main
if __name__ == '__main__':
	if len(sys.argv) != 3:
		print("Error: Wrong usage!")
		print("Usage: python3 GameClient.py <Server_addr> <Server_port>")
		sys.exit(1)
	main(sys.argv)