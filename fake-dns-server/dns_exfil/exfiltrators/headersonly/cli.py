import click
from dns_exfil.exfiltrators.headersonly.server import HeaderAppendResolver
from dns_exfil.exfiltrators.base.server import start_server
from dns_exfil import config


@click.command()
@click.option('--ip', default=config['server']['headerappendresolver']['ip'],
              help='spoof IP address to use in server responses')
@click.option('--basedir', default=config['server']['headerappendresolver']['basedir'],
              help='Where the files should be saved')
def headersonly(ip, basedir):
    context = config['server']['headerappendresolver']
    context.update(locals())
    start_server(HeaderAppendResolver())
