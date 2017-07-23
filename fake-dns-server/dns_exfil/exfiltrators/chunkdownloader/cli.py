from dns_exfil.exfiltrators.chunkdownloader.client import ChunkClient

@click.command(name='download')
@click.option('--chunk_size', help='size in bytes to transfer in each packet', default=30, type=int)
@click.option('--domain', default='example.com', help='ending domain name')
@click.argument('connect')
@click.argument('filename')
def chunk_download(chunk_size, domain, connect, filename):
    client = ChunkClient(domain, connect)
    client.download(filename, chunk_size)

@click.command(name='list')
@click.option('--domain', default='example.com', help='ending domain name')
@click.argument('connect')
def chunk_list(domain, connect):
    client = ChunkClient(domain, connect)
    index = client.get_index()
    for element in index:
        print(element['name'])

@click.command(name='upload')
@click.option('--chunk_size', help='size in bytes to transfer in each packet', default=30, type=int)
@click.option('--domain', default='example.com', help='ending domain name')
@click.argument('connect')
@click.argument('filename')
def chunk_upload(chunk_size, domain, connect, filename):
    client = ChunkClient(domain, connect)
    client.upload(filename, chunk_size)

@click.group()
def chunk_client(name='chunk'):
    pass


chunk_client.add_command(chunk_download)
chunk_client.add_command(chunk_list)
chunk_client.add_command(chunk_upload)
