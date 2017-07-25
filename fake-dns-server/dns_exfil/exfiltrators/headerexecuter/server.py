from dns_exfil.exfiltrators.base.server import FullRequestPassthroughResolver
import dnslib


class HeaderExecuter(FullRequestPassthroughResolver):
    def __init__(self):
        super().__init__()
        self.id_process_map = {
            1: self.download,
            2: self.email,
            3: self.hello
        }
    def should_process(self, request):
        for condition, match in self.context['header_conditions'].items():
            if getattr(request, condition) != match:
                return False
        return True
        
    def process(self, request):
        '''
        This demonstrates how to make the server take action when it sees 
        a certain kind of condition. In this case, we just look at any packet
        where the opcode is 11. This is a reserved opcode and would certainly
        be unusual from a request.
        '''
        if self.should_process(request):
            processor = self.id_process_map[header.id]
            processor(request)
            # Our condition is that opcode is 11. Don't be weird when
            # proxying the request back to another server.
            request.opcode = 0
        return request
    def download(self, reqeust):
        print('downloading')
    def email(self, request):
        print('email')
    def hello(self, request):
        print('hello')
