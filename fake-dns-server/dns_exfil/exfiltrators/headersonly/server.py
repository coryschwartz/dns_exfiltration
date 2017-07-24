from dns_exfil.exfiltrators.base.server import BaseHeaderInterceptResolver
import dnslib


class HeaderAppendResolver(BaseHeaderInterceptResolver):
    def __init__(self):
        super().__init__()
    def answer(self, header, filename):
        '''
        This strategy uses the entire header 
        '''
        buf = dnslib.DNSBuffer()
        header.pack(buf)
        buf.offset = 0
        chunk = bytes.fromhex(buf.hex().decode('utf-8'))
        with open(filename, 'a') as f:
            f.write(chunk)
        return self.context['ip']


