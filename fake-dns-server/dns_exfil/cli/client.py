import click

from dns_exfil.exfiltrators.chunkdownloader.cli import chunk_client
from dns_exfil.exfiltrators.botexfiltrator.cli import bot_client

import sys
import base64
import time

import dnslib
       

@click.group()
def main():
    pass


main.add_command(bot_client)
main.add_command(chunk_client)
