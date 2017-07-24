from dns_exfil.exfiltrators.botexfiltrator.server import BotExfiltrator
from dns_exfil.exfiltrators.chunkdownloader.server import ChunkDownloader
from dns_exfil.exfiltrators.headersonly.cli import headersonly
from dns_exfil.exfiltrators.base.server import start_server
from dns_exfil import config

import click
import os

@click.command()
@click.option('--domain', default=config['server']['botexfiltrator']['domain'],
              help='spoof Domain name to use in server responses')
@click.option('--ip', default=config['server']['botexfiltrator']['ip'],
              help='spoof IP address to use in server responses')
@click.option('--cmd', default=config['server']['botexfiltrator']['cmd'],
              help='File for sending commands through MX records')
@click.option('--basedir', default=config['server']['botexfiltrator']['basedir'],
              help='Where the files should be saved')
def bot(domain, ip, cmd, basedir):
    context = config['server']['botexfiltrator']
    context.update(locals())
    start_server(BotExfiltrator())

@click.command()
@click.option('--ttl', default=config['server']['chunkdownloader']['ttl'],
              help='Time To Live request for DNS caches')
@click.option('--basedir', default=config['server']['chunkdownloader']['basedir'],
              help='Where files should be served from')
def chunk(basedir, ttl):
    context = config['server']['chunkdownloader']
    context.update(locals())
    start_server(ChunkDownloader())

@click.group()
def main():
    pass

main.add_command(bot)
main.add_command(chunk)
main.add_command(headersonly)
