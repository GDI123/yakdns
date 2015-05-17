import socket
import sys
import time
import os
sys.path.append("contrib/python/")
import cjdnsadmin.adminTools as at
sys.path.append("contrib/python/cjdnsadmin")
from publicToIp6 import PublicToIp6_convert
sys.path.append('')

peerstats_result = []

filescheck_dnsdb = os.path.exists("dns.db") #file check here
if filescheck_dnsdb != True:
	print "dns.db not found - creating now"
	with open("dns.db",'w'):
		pass

with open("dns.db",'r') as dns_list:
	pre_ip_dns_list = dns_list.readlines()
ip_dns_list = {}
for x in pre_ip_dns_list:
	temp = x.split()
	print temp
	if len(temp) != 0:
		ip_dns_list[temp[0].strip()] = [temp[1].strip(),temp[2].strip(),temp[3].strip()]

def check_db_current():#this monster basicly searches and asks if anyone would like to sync with it, and it checks if everything is right with a couple of mega simple algorithms
	recieved_dns_list = []
	#start temp server
	try:
		s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		s.settimeout(10)
		s.bind(('::', 8878))
		s.listen(1)
		#request sync
		send_sync_request(peerstats_result,"00")
		#wait and accept a connection
		conn, addr = s.accept()
		s.settimeout(None)
		bob = conn.recv(1024)
		print bob
		if bob.strip() == "ready":
			i = 0
			#have to add an if db empty send all your database
			print len(ip_dns_list)
			if len(ip_dns_list) != 0:
				t_stamp = get_newest_timestamp(ip_dns_list)
			else:
				t_stamp = 0
			print "final t-stamp result" + str(t_stamp)
			conn.send(str(t_stamp))
			print "timestamp sent"
			while i != 1:
				r_Data = conn.recv(2048)
				if r_Data.strip() != "done":
					recieved_dns_list.append(r_Data)
					conn.send("go")
				else:
					i = 1

				s.close()

		if len(recieved_dns_list) != 0:
			final_list = {}
			for x in recieved_dns_list:
				temp = x.split()
				final_list[temp[0].strip()] = [temp[1].strip(),temp[2].strip(),temp[3]]

			print "final list: " + str(final_list)
			new = sync_db_check(ip_dns_list,final_list)
			print "sync completed now writing to database"
			with open("dns.db",'w') as update:
				for x in new:
					update.write(x + " " + new[x][0] + " " + new[x][1] + " " + new[x][2] + "\n")

			print "all done starting up ddns"
		else:
			print "nothing to update, continuing to start ddns"
	except:
		print "no other dns servers found, continuing to start ddns"

def get_newest_timestamp(old):#search current dns list for the newest entry
	newest_timestamp = []
	for x in old:
		newest_timestamp.append(old[x][1])
	last_timestamp = max(newest_timestamp)
	return last_timestamp


def get_newest_entrys(current_dict,timestamp_request):#this is used to grab only the newest dns entrys from a specified date
	newest = []
	for x in current_dict:
		if current_dict[x][1] > timestamp_request:
			newest.append(str(x) + " " + str(current_dict[x][0]) + " " + str(current_dict[x][1]) + " " + str(current_dict[x][2]))
	return newest

def sync_db_check(old,new):#compares local dns list and requested new one and updates entrys to match
	for x in new:
		if x not in str(old):
			old[x] = new[x]
		elif old[x][1] != new[x][1]: #this if statement checks and compares to see if timestamps are the same or not
			if old[x][2] < new[x][2]: #this if statement checks to see if times update is greater than in the original dictonary if so it will update the old dictonary to match
				old[x] = new[x] #update old dict
	return old

def get_peerstats():#find out who were connected to so we can find dns servers
	cjdns=at.anonConnect()
	peerstats_raw = at.peerStats(cjdns,verbose=False);
	cjdns.disconnect()
	global peerstats_result
	for x in peerstats_raw:
		peerstats_result.append(PublicToIp6_convert(x['publicKey']))
	print "peerstats" + str(len(peerstats_result))

def send_sync_request(servers,data_to_send):
	i = 0
	b = 0
	while b != 2:
		for x in servers:
			client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
			client.connect((x.strip(), 8787))
			client.send(data_to_send)
			i = i + 1
			print "attempt" + str(i)
		b = b + 1
def send_to_peers(server_list,data_to_send):#relay request to any available servers using peerstat data and once request has been processed
	#consider butchering the "findnode" code in cjdns to fall back on to find more dns servers
	for x in server_list:
		print x
		if x != addr[0]:
			client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
			#consider sending 3 times if no responce move on to next node
			#client.settimeout(1)
			b = 0
			while b != 2:
				client.sendto(data_to_send, (x.strip(), 8787))
				b = b + 1
			#add in wait and comfirm send, and settimeout as well if nothing recieved

def check_for_bad_symbols(request):
	temp = request.split()
	bool_list = []
	bool_list.append(temp[1].replace(".","").replace("-","").isalnum())
	bool_list.append(temp[2].replace(":","").isalnum())
	bool_list.append(temp[3].replace(".","").isdigit())
	bool_list.append(temp[4].isdigit())

	if False in bool_list:
		return False
	else:
		return True

def new_db_request(address): #request to syncronise with another dns server
	time.sleep(1)
	try:
		client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		client.connect((address, 8878))
		client.send("ready")
		timestamp_to_check_from = client.recv(1024)
		print "recieve timestamp: " + str(timestamp_to_check_from)
		to_be_synced = get_newest_entrys(ip_dns_list,timestamp_to_check_from)
		print "list to be synced: " + str(to_be_synced)
		if len(to_be_synced) != 0:
			print "sending data for syncing"
			for x in to_be_synced:
				temp = x.split()
				client.send(str(temp[0].strip()) + " " + str(temp[1].strip()) + " " + str(temp[2].strip()) + " " + str(temp[3].strip()))
				go = client.recv(1024)
			client.send("done")
		else:
		 	client.send("done")
		 	print "nothing to sync"
			print "finished"
			client.close()
	except:
		print "coudlnt connect"

def new_dom(data):# adds a new entry in dns.db
	get_peerstats()
	new_dom_array = data.split()
	if new_dom_array[1] not in ip_dns_list:
		print "1"
		ip_dns_list[new_dom_array[1]] = [new_dom_array[2], new_dom_array[3], 1] #check and change
		with open("dns.db",'w') as handler:
			for x in ip_dns_list:
				handler.write(str(x) + " " + str(ip_dns_list[x][0]) + " " + str(ip_dns_list[x][1]) + " " + str(ip_dns_list[x][2]) + "\n")
		send_to_peers(peerstats_result, data)
		print "new dom accepted"
		udoser.sendto("New Domain Added",addr)

	elif ip_dns_list[new_dom_array[1]][0] == "x":
		print "2"
		ip_dns_list[new_dom_array[1]] = [new_dom_array[2], new_dom_array[3], str(int(ip_dns_list[new_dom_array[1]][2]) + 1)] #check and change
		with open("dns.db",'w') as handler:
			for x in ip_dns_list:
				handler.write(str(x) + " " + str(ip_dns_list[x][0]) + " " + str(ip_dns_list[x][1]) + " " + str(ip_dns_list[x][2]) + "\n")
		send_to_peers(peerstats_result, data)
		print "new dom accepted"
		udoser.sendto("New Domain Added",addr)
	else:
		print "3"
		udoser.sendto("Domain Already Taken",addr)

def release_dom(data): #simply removes an entry in the dns.dn
	get_peerstats()
	rel_dom_array = data.split()
	if rel_dom_array[1] in ip_dns_list:
		if ip_dns_list[rel_dom_array[1]][0] != "x":
			ip_dns_list[rel_dom_array[1]] = ["x",str(time.time()),str(int(ip_dns_list[rel_dom_array[1]][2]) + 1)]
			print "domain released"
			with open("dns.db",'w') as handler:
				for x in ip_dns_list:
					handler.write(str(x) + " " + str(ip_dns_list[x][0]) + " " + str(ip_dns_list[x][1]) + " " + str(ip_dns_list[x][2]) + "\n")
			send_to_peers(peerstats_result, data)
			print "domain released + w"
			udoser.sendto("Domain Released",addr)
		else:
			print "domain already released"
			udoser.sendto("domain already released",addr)
	else:
		udoser.sendto("Does not exist",addr)
get_peerstats()
check_db_current()
server = "::" #ipv6 localaddr
#this section is the server its self
udoser = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
port_number = 8787
udoser.bind((server, port_number))
i=0
while i == 0:
   	global addr
	request, addr = udoser.recvfrom(2048)
   	if request == None:
		break
	print "incoming request: " + request + " - from: " + str(addr[0])
	#this section deals with all the requests that come in, including requests to syncronise databases
	#udoser.sendto("ok",addr)
	s_request = request.split()
	if 01 == int(s_request[0]):
		if check_for_bad_symbols(request) != False:
			print "here"
			new_dom(request)
		else:
			udoser.sendto("Bad Symbols in Request",addr)
	if 02 == int(s_request[0]):
		release_dom(request)
	if 00 == int(s_request[0]):
		new_db_request(addr[0])
