# ddns
a very basic attempt at decentralised dns for cjdns

Ddns piggy backs Cjdns's dht routing to find servers to share dns data with, this way we dont have to create our own dht program. 

DDNS is ready for testing, This is PRE-ALPHA, so lots of broken shit

# Install ddns

simply drop ddns.py into /cjdns-master thats it and run as root just like cjdns

client:

client can be run as normal user from anywhere

Add new domain: python ddns-client.py new domain.name ipv6-addr
Rlease a domain: python ddns-client.py release domain.name

# How it works

Domains are stored in dns.db as follows:

"example.com ipv6-addr timestamp change-counter"

"io.nerd fc38:410e:bce7:a7e2:d4f0:a805:b509:be11 1431803121.12 0"

request format should be as follows, and over udp:

01 = add new domain

01 io.nerd fc38:410e:bce7:a7e2:d4f0:a805:b509:be11 1431803121.12 0

02 = release domain

02 io.nerd (the server will deal with releasing the domain)

00 = is a sync request, this is only done by the servers when they start up not the client

# contact

you can find me on irc at  yakamo.org #ddns

Todo list:
==========

threading & queueing for incoming requests

possibly treat ddns like cjdns in that you have to accept or add other nodes in the trust format/ this would simplifie a few things and, maybe have ddns search your config file and grab the public key and convert it to the ipv6 and use that so the user doesnt have to configure it them self??????

fix sync client* done

  add option to do a manual sync after startup
  
add request confirmation and timeout

away for the host machine to use the dns.db, either through dumping it to /etc/hosts or creating something that the system can query for dns.

and of course a client for making these requests

create a manual for how to interact with the ddns server for developers

figure weather to use sqlite or json to create the database
