import os
import sys
import socket
import logging
import urllib
import imp
import traceback
#
from .web import Web
from .conf import Config
import irc
import mod_importer


class Bot(object):

    def __init__(self, name='Bot Bot Bot', nick='ivory',
                 network='localhost', port=6667, skynet=None,
                 modules_dir=os.path.normpath('./modules'),
                 config_path='~/.ivory/default.py'):
        self.name = name
        self.nick = nick
        self.network = network
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command = irc.Command(self.sock)
        r, w = os.pipe()
        self.buffer_r_last = ''
        self.buffer_r = r
        self.buffer_w = w
        self.skynet = skynet
        self.channels = []
        # Config
        self.config_path = os.path.abspath(os.path.expanduser(config_path))
        self.config = None
        # Load the modules
        self.modules_dir = os.path.abspath(modules_dir)
        self.modules = None
        self.actions = None
        self.reload()

    def __getattr__(self, name):
        try:
            return getattr(self, name)
        except:
            return getattr(self.skynet, name)

    def reload(self):
        try:
            self.config = Config(self.config_path)
        except Exception, e:
            logging.error('Error reloading config: path=%s', self.config_path)
            logging.error(traceback.format_exc())
        try:
            m = mod_importer.load_module(self.modules_dir)
            self.modules = mod_importer.get_modules(m)
            self.actions = mod_importer.process_modules(self.modules)
            logging.info('Loaded actions:')
            for a in self.actions:
                logging.info('> %r', a)
        except Exception, e:
            logging.error('Error reloading mods: path=%s', self.modules_dir)
            logging.error(traceback.format_exc())

    def fileno(self):
        return self.sock.fileno()

    def connect(self):
        self.sock.connect((self.network, self.port))
        self.command.nick(self.nick)
        self.command.user(self.nick, self.nick, self.nick, self.name)

    def join(self, *channels):
        self.command.join(channels)
        self.channels.extend(channels)

    def die(self):
        self.command.part(self.channels)
        self.command.quit()
        self.sock.close()

    def run(self):
        pass

    def handle(self, event):
        os.write(self.buffer_w, self.sock.recv(4096))
        self.handle_line()

    def handle_line(self):
        all = os.read(self.buffer_r, 4096)
        lines = all.split('\r\n')

        lines[0] = self.buffer_r_last + lines[0]
        if not lines[-1]:
            self.buffer_r_last = lines[-1]
            lines = lines[:-1]
        else:
            self.buffer_r_last = ''

        for line in lines:
            self.parse_ping(line) or self.parse_other(line)

    def parse_ping(self, line):
        x = line.split(' ')
        if x and x[0] == 'PING':
            self.command.pong(' '.join(x[1:]))
            return True
        return False

    def wrapped(realself, info, nick):
        class Wrapper(object):
            def __init__(self):
                self.bot = realself
                self.sender = nick
                self.is_channel = False
                if info[2].startswith('#'):
                    self.sender = info[2]
                    self.is_channel = True

            def reply(self, msg):
                return self.say('%s: %s' % (nick, msg))

            def say(self, msg):
                return self.bot.command.msg(self.sender, msg)

            def __getattr__(self, name):
                if name == 'reply':
                    return self.reply
                elif name == 'say':
                    return self.say
                return getattr(self.bot, name)
        return Wrapper()

    def parse_other(self, line):
        logging.debug(line)
        all = line.split(':')
        if len(all) > 1:
            info = all[1].split()
            nick = info[0].split('!')[0]
            other = ':'.join(all[2:])
            # If from self, stop.
            if nick == self.nick:
                return
            if len(info) > 2 and info[1] == 'PRIVMSG':
                wrapped = lambda: self.wrapped(info, nick)
                for action in self.actions:
                    if action(wrapped, other):
                        break
