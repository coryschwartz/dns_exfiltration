import click
from dns_exfil.exfiltrators.headerexecuter.server import HeaderExecuter
from dns_exfil.exfiltrators.base.server import start_server
from dns_exfil import config


@click.command(name='executer')
def headerexecuter():
    context = config['server']['headerexecuter']
    context.update(locals())
    start_server(HeaderExecuter())
