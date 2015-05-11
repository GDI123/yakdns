import socket
import sys
import time
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

	client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	client.bind(("::", 8788))
	client.listen(1)
	conn, addr = s.accept()

	#client.settimeout(5)
	send_sync_request(peerstats_result,"00")

	incoming_data = conn.recv(1024)

	print incoming_data
	if incoming_data.strip() == "00ok":
		from_this_timestamp = get_newest_timestamp(ip_dns_list)
		print "last entry" + str(from_this_timestamp) 
		conn.send(from_this_timestamp)
		wait = conn.recv(1024)
		if wait != "00utd":
			i = 0
			while i == 0:
				recieved_data = conn.recv(1024)
				if recieved_data != "00done":
					recieved_dns_list.append(recieved_data)
				else:
					client.close()
					i = 1

			final_list = {}
			for x in recieved_dns_list:
				temp = x.split()
				final_list[temp[0].strip()] = [temp[1].strip(),temp[2].strip(),temp[3]]

			new = sync_db_check(ip_dns_list,final_list)

			with open("dns.db",'w') as update:
				for x in new:
					update.write(x + new[x][0] + new[x][1] + new[x][2] + "\n")
		else:
			print "nothing to update"

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
			newest.append(current_dict[x] + current_dict[x][0] + current_dict[x][1] + current_dict[x][2])
	return newest

def sync_db_check(old,new):#compares local dns list and requested new one and updates entrys to match
	for x in new:
		if old[x][1] != new[x][1]: #this if statement checks and compares to see if timestamps are the same or not
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
	print len(peerstats_result)

def send_sync_request(servers,data_to_send):
	i = 0
	for x in servers:
		client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
		client.connect((x.strip(), 8787))
		client.send(data_to_send)
		i = i + 1
		print "attempt" + str(i)

def send_to_peers(server_list,data_to_send):#relay request to any available servers using peerstat data and once request has been processed
	for x in server_list:
		print x
		if x != addr[0]:
			client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
			client.connect((x.strip(), 8787))
			client.send(data_to_send)
		print data_to_send

def new_db_request(address): #request to syncronise with another dns server
	client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	client.connect((address, 8788))
	client.send("00ok")
	timestamp_to_check_from = client.recv(1024)
	to_be_synced = get_newest_entrys(ip_dns_list,timestamp_to_check_from)
	if len(to_be_synced) != 0:
		for x in to_be_synced:
			client.send(to_be_synced[x].strip() + to_be_synced[x][0].strip() + to_be_synced[x][1].strip() + to_be_synced[x][2].strip())
	else:
	 	client.sendto("00utd")
	client.send("00done")
	client.close()

def new_dom(data):# adds a new entry in dns.db
	get_peerstats()
	new_dom_array = data.split()
	if new_dom_array[1] not in ip_dns_list:
		ip_dns_list[new_dom_array[1]] = [new_dom_array[2], new_dom_array[3], 1] #check and change
		with open("dns.db",'w') as handler:
			for x in ip_dns_list:
				handler.write(str(x) + " " + str(ip_dns_list[x][0]) + " " + str(ip_dns_list[x][1]) + " " + str(ip_dns_list[x][2]) + "\n")
		send_to_peers(peerstats_result, data)
		print "new dom accepted"
		udoser.sendto("New Domain Added",addr)

	elif ip_dns_list[new_dom_array[1]][0] == "x":
		ip_dns_list[new_dom_array[1]] = [new_dom_array[2], new_dom_array[3], str(int(ip_dns_list[new_dom_array[1]][2]) + 1)] #check and change
		with open("dns.db",'w') as handler:
			for x in ip_dns_list:
				handler.write(str(x) + " " + str(ip_dns_list[x][0]) + " " + str(ip_dns_list[x][1]) + " " + str(ip_dns_list[x][2]) + "\n")
		send_to_peers(peerstats_result, data)
		print "new dom accepted"
		udoser.sendto("New Domain Added",addr)
	else:
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
check_db_current("::")
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
	s_request = request.split()
	if 01 == int(s_request[0]):
		new_dom(request)
	if 02 == int(s_request[0]):
		release_dom(request)
	if 00 == int(s_request[0]):
		new_db_request(addr[0])
