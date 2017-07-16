from os import getcwd

# This is a module-wide config dictionary
# It changes according to commandline arguments

config = {
    'server': {
        'service': {
            'listen': 0.0.0.0
        },
        'bot': {
            'domain': 'def.con',
            'ip': '192.168.1.1',
            'cmd': 'cmd',
            'basedir': getcwd()
        },
    },
    'client': {
    },
}
