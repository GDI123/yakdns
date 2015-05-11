# ddns
a very basic attempt at decentralised dns for cjdns

Ddns piggy backs Cjdns's dht routing to find servers to share dns data with, this way we dont have to create our own dht program. 

THIS IS NOT FOR USE AT THE MOMENT, STILL IN A BROKEN STATE.

Todo list:
==========

threading & queueing for incoming requests

fix sync client

add request confirmation and timeout

add a check if dns.db exists if not create

error checking for bad symbols in any of following: domain, ip, timestamp and change counter

away for the host machine to use the dns.db, either through dumping it to /etc/hosts or creating something that the system can query for dns.

and of course a client for making these requests

create a manual for how to interact with the ddns server for developers

figure weather to use sqlite or json to create the database
