from dns_exfil.exfiltrators.base.server import FullRequestInterceptResolver
import dnslib


class HeaderAppendResolver(FullRequestInterceptResolver):
    def __init__(self):
        super().__init__()
    def answer(self, request):
        '''
        This strategy uses the entire header 
        '''
        print(request)
        return self.context['ip']
