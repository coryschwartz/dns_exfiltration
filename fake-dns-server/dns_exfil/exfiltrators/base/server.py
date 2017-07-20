import sys
from functools import wraps

from dns_exfil import config

import dnslib
from dnslib.server import DNSServer, BaseResolver
from dnslib.intercept import InterceptResolver

# The two classes defined here are raised when a subclass fails to define
# an exfiltration method for the query requested (RecordTypeNotDefined)
# or when the record type is defined but the query fails to exfiltrate
# acording to our protocol (CannotExfiltrateError). In both cases, the server
# should revert back to default behavior.
# Any other error that comes up, such as filesystem errors, etc. are caught
# and logged to stderr. It's not usually good to just catchall like this. whatever.

class RecordTypeNotDefined(Exception):
    pass

class CannotExfiltrateError(Exception):
    pass

def printerrors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as e:
            message = '::- Server Error -:: '
            if len(e.args) > 0:
                message = message + e.args[0]
            sys.stderr.write(message)
            errheader = dnslib.DNSHeader(rcode=RCODE.SERVFAIL)
            err = dnslib.DNSRecord(header=errheader)
            return err
    return wrapper


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
        # For example, QTYPE[15] -> 'MX', and QTYPE.MX -> 15.
        # See https://en.wikipedia.org/wiki/List_of_DNS_record_types
        # If a class has a method implemented by this name, we can use it
        # otherwise, we will just proxy the request upstream.
        try:
            query_resolver = getattr(self, dnslib.QTYPE[qtype])
            rdata_handler = getattr(dnslib, dnslib.QTYPE[qtype])
        except AttributeError:
            raise RecordTypeNotDefined
        question_name = str(qname)
        # Subclasses should raise CannotExfiltrateError. This should be raised,
        # for example, if the query is in the incorrect format or if the server
        # encounters some other kind of problem with the query.
        response = query_resolver(question_name)
        answer = dnslib.RR(question_name, qtype, rdata=rdata_handler(response), ttl=self.context['ttl'])
        return answer
        
    @printerrors
    def resolve(self, request, handler):
        try:
            reply = request.reply()
            reply.add_answer(self.answer(request.q.qname, request.q.qtype))
            return reply
        except (RecordTypeNotDefined, CannotExfiltrateError):
            return self.interceptor.resolve(request, handler)



class InterceptAppendResolver(InterceptDefaultResolver):
    '''
    Always resolve a request from upstream.
    If it's possible to answer a question, add the response at the end.
    '''
    def __init__(self):
        super().__init__()

    @printerrors
    def resolve(self, request, handler):
        qname = request.q.qname
        qtype = request.q.qtype
        try:
            answer = self.answer(qname, qtype)
            # We answered the question without an error, so we are exfiltrating successfully
            # When this happens, we want to proxy back the real domain name to get back real data
            # with our fake response inconspicuously at the end.
            real_domain_name = '.'.join(str(qname).split('.')[-3:])
            real_request = dnslib.DNSRecord()
            real_request.add_question(dnslib.DNSQuestion(real_domain_name, qtype))
            real_reply = self.interceptor.resolve(real_request, handler)

            # Build a new record which has the ID and question of the original question
            # and the answers from both real and fake sources.
            return_reply = dnslib.DNSRecord()
            return_reply.header.id = request.header.id
            return_reply.add_question(request.q)
            return_reply.add_answer(real_reply.a)
            return_reply.add_answer(answer)
        except (RecordTypeNotDefined, CannotExfiltrateError):
            # if we are here, we did not exfiltrate data.
            # Lets assume it's a real domain and just return a valid response
            return_reply = self.interceptor.resolve(request, handler)
        return return_reply


def start_server(resolver):
    server = DNSServer(resolver=resolver, **config['server']['service'])
    server.start()
