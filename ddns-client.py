#temp ddns request client
import sys
import socket
import time
server = "::"
if sys.argv[1] == "new":
	data_to_send = "01 " + str(sys.argv[2]) + " " + sys.argv[3] + " " + str(time.time()) + " 0"
elif sys.argv[1] == "release":
	data_to_send = "02 " + sys.argv[2]
else:
	print "what? try again you fat fingered fuck"

client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
client.connect((server, 8787))
client.send(data_to_send)
print client.recv(1024)
