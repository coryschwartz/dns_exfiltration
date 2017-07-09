import click
import os

@click.command()
@click.option('--domain', default='def.con', help='spoof Domain name to use in server responses')
@click.option('--ip', default='192.168.1.1', help='spoof IP address to use in server responses')
@click.option('--cmd', default='cmd', help='File for sending commands through MX records')
@click.option('--basedir', default=os.getcwd())
def bot(domain, ip, cmd, basedir):
    print('DNS exfil Server Bot')
    print(locals())


@click.group()
def main():
    pass

main.add_command(bot)
