

class Command(object):

    def __init__(self, sock):
        self.sock = sock

    def send_command(self, command, *args):
        #print '%s %s' % (command, ' '.join(args))
        self.sock.send('%s %s\r\n' % (command, ' '.join(args)))

    def password(self, passwd):
        self.send_command('PASS', passwd)

    def nick(self, nickname):
        self.send_command('NICK', nickname)

    def user(self, username, hostname, servername, realname):
        self.send_command('USER', username, hostname, servername,
                          ':%s' % realname)

    def oper(self, user, passwd):
        self.send_command('OPER', user, passwd)

    def quit(self, message='Bye.'):
        self.send_command('QUIT', ':%s' % message)

    def join(self, channels, keys=None):
        if not channels:
            return
        if not keys:
            keys = []
        self.send_command('JOIN', ','.join(channels), *keys)

    def part(self, channels, message='Bye.'):
        if not channels:
            return
        self.send_command('PART', ','.join(channels), ':%s' % message)

    def channel_mode(self, modeline, limit=None, user=None, banmask=None):
        pass
        # XXX TODO

    def user_mode(self, nick, mode):
        pass
        # XXX TODO

    def names(self, channels):
        if not channels:
            return
        self.send_command('NAMES', ','.join(channels))

    def list(self, channels=None, server=None):
        if not channels:
            self.send_command('LIST')
        self.send_command('LIST', ','.join(channels))

    def invite(self, nick, channel):
        self.send_command('INVITE', nick, channel)

    def kick(self, channel, user, comment=''):
        self.send_command('KICK', channel, user, comment)

    def connect(self, server, port='6667', remote=None):
        self.send_command('CONNECT', server, port)

    def msg(self, receiver, *args):
        if not args:
            return
        r = [receiver]
        r.extend(args[:-1])
        self.send_command('PRIVMSG', ','.join(r), ':%s' % args[-1])

    def notice(self, nickname, text):
        self.send_command('NOTICE', nickname, ':%s' % text)

    def ping(self, server1, server2=None):
        pass

    def pong(self, daemon1, daemon2=None):
        self.send_command('PONG', daemon1)

    # TRACE
    # ADMIN
    # ERROR
    # WHO
    # WHOIS
    # WHOWAS
    # INFO
    # VERSION
    # STATS
