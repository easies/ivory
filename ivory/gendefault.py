import os
import sys


def get_default(moddir):
    return """\
nick = 'ivory'
name = 'Ivory Bot'
modules = '%(moddir)s'
host = 'irc.example.com'
port = 6667
channels = ['#test']
owner = '' # your username here
# trusted people
admins = [owner]
""" % locals()


def main(path, moddir):
    path = os.path.expanduser(path)
    directory = os.path.dirname(path)
    sys.stdout.write('Generating default config at %s\n' % path)
    if os.path.exists(path):
        sys.stderr.write('Error: %s already exists.\n' % path)
        return
    if not os.path.isdir(directory):
        os.makedirs(os.path.dirname(path), 0700)
    with open(path, 'wb') as f:
        f.write(get_default(moddir))
    sys.stdout.write('Done.\n')


if __name__ == '__main__':
    main('~/.ivory/default.py')
