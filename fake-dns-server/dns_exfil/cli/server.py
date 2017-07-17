from dns_exfil.server import BotExfiltrator, start_server
from dns_exfil import config

import click
import os


@click.command()
@click.option('--domain', default=config['server']['bot']['domain'],
              help='spoof Domain name to use in server responses')
@click.option('--ip', default=config['server']['bot']['ip'],
              help='spoof IP address to use in server responses')
@click.option('--cmd', default=config['server']['bot']['cmd'],
              help='File for sending commands through MX records')
@click.option('--basedir', default=config['server']['bot']['basedir'],
              help='Where the files should be saved')
def bot(domain, ip, cmd, basedir):
    context = config['server']['botexfiltrator']
    context.update(locals())
    start_server(config['server']['service']['listen'], BotExfiltrator)


@click.group()
def main():
    pass

main.add_command(bot)
