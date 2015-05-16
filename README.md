# ddns
a very basic attempt at decentralised dns for cjdns

Ddns piggy backs Cjdns's dht routing to find servers to share dns data with, this way we dont have to create our own dht program. 

THIS IS NOT FOR USE AT THE MOMENT, STILL IN A BROKEN STATE.

Todo list:
==========

threading & queueing for incoming requests

possibly treat ddns like cjdns in that you have to accept or add other nodes in the trust format/ this would simplifie a few things and, maybe have ddns search your config file and grab the public key and convert it to the ipv6 and use that so the use doesnt have to configure it them self??????

fix sync client* done

  add option to do a manual sync after startup
  
  new_db_request needs to exit correctly

add request confirmation and timeout

away for the host machine to use the dns.db, either through dumping it to /etc/hosts or creating something that the system can query for dns.

and of course a client for making these requests

create a manual for how to interact with the ddns server for developers

figure weather to use sqlite or json to create the database
