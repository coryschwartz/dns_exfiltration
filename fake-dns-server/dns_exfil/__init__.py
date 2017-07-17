from os import getcwd

# This is a module-wide config dictionary
# It changes according to commandline arguments

config = {
    'server': {
        # Settings for this server
        'service': {
            'address': '0.0.0.0',
            'port': 53,
            'tcp': False
        },
        # https://github.com/paulchakravarti/dnslib/blob/github/dnslib/intercept.py#L16
        'upstream': {
            'address': '8.8.8.8',
            'port': 53,
            'ttl': '60s',
            'intercept': [],
            'skip': [],
            'nxdomain': [],
            'timeout': '5s'
        },
        'botexfiltrator': {
            'domain': 'def.con',
            'ip': '192.168.1.1',
            'cmd': 'cmd',
            'basedir': getcwd(),
            'ttl': 0
        },
    },
    'client': {
    },
}
