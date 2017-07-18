from dns_exfil.exfiltrators.base.server import InterceptAppendResolver

class ChunkDownloader(InterceptAppendResolver):
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
        return_fields = fields[3:]
        return_fields.insert(0, encoded_data.decode('utf-8'))
        return '.'.join(return_fields)

    def TXT(self, name):
        '''
        This is the 'index' of the service.
        It it prints the names and size of the files being served.
        '''
        base = self.context['basedir']
        fileinfo = [','.join([fn, str(os.stat(fn).st_size)]) for fn in os.listdir(base)]
        index = ';'.join(fileinfo)
        return index
 