from dns_exfil import config

import dnslib
from dnslib.server import DNSServer, BaseResolver
from dnslib.intercept import InterceptResolver

class RecordTypeNotDefined(Exception):
    pass

class InterceptDefaultResolver(BaseResolver):
    '''
    If a record type is defined by a subclass, use that method to resovlve answers
    If not, pass the request up to the upstream server
    '''
    def __init__(self):

        self.interceptor = InterceptResolver(**config['server']['upstream'])
        # link the piece of global config relevant to this instance
        context_name = type(self).__name__.lower()
        self.context = config['server'][context_name]
        super().__init__()

    def answer(self, qname, qtype):
        # The QTYPE bitmaps numerical record types to it's string value
        # For example, QTYPE[15] -> 'MX'
        # See https://en.wikipedia.org/wiki/List_of_DNS_record_types
        # If a class has a method implemented by this name, we can use it
        # otherwise, we will just proxy the request upstream.
        try:
            query_resolver = getattr(self, dnslib.QTYPE[qtype])
            rdata_handler = getattr(dnslib, dnslib.QTYPE[qtype])
        except AttributeError:
            raise RecordTypeNotDefined
        question_name = str(qname)
        response = query_resolver(question_name)
        answer = dnslib.RR(question_name, qtype, rdata=rdata_handler(response), ttl=self.context['ttl'])
        return answer
        
    def resolve(self, request, handler):
        try:
            reply = request.reply()
            reply.add_answer(self.answer(request.q.qname, request.q.qtype))
            return reply
        except:
            return self.interceptor.resolve(request, handler)

class InterceptAppendResolver(InterceptDefaultResolver):
    '''
    Always resolve a request from upstream.
    If it's possible to answer a question, add the response at the end.
    '''
    def __init__(self):
        super().__init__()

    def resolve(self, request, handler):
        try:
            qname = request.q.qname
            qtype = request.q.qtype
            answer = self.answer(qname, qtype)
            # We answered the question without an error, so we are exfiltrating successfully
            # When this happens, we want to proxy back the real domain name to get back real data
            # with our fake response inconspicuously at the end.
            real_domain_name = '.'.join(str(qname).split('.')[-2:])
            real_request = request
            real_request.q = dnslib.DNSQuestion(real_domain_name, qtype)
            reply = self.interceptor.resolve(real_request, qtype), handler)
            reply.add_answer(answer)
        except:
            reply = self.interceptor.resolve(request, handler)
            pass
        return reply


def start_server(resolver):
    server = DNSServer(resolver=resolver, **config['server']['service'])
    server.start()
