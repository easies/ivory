import os
import re
import sys
import socket
import logging
import urllib
import imp
import traceback
#
from .web import Web
from .conf import Config
from .action import Action
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
        self.command = irc.Command(self.sock, self)
        r, w = os.pipe()
        self.buffer_r_last = ''
        self.buffer_r = r
        self.buffer_w = w
        self.skynet = skynet
        self.channels = []
        self.callbacks = {}
        # Config
        self.config_path = os.path.abspath(os.path.expanduser(config_path))
        self.config = None
        # Load the modules
        self.modules_dir = os.path.abspath(modules_dir)
        self.modules = None
        self.actions = None
        self.reload(True)

    def __getattr__(self, name):
        try:
            return getattr(self, name)
        except:
            return getattr(self.skynet, name)

    def add_callback(self, op, cb):
        try:
            self.callbacks[op].append(cb)
        except KeyError:
            self.callbacks[op] = [cb]

    def pop_callback(self, op):
        try:
            return self.callbacks[op].pop()
        except:
            pass

    def reload(self, _init=False):
        errors = False
        try:
            self.config = Config(self.config_path)
        except Exception, e:
            logging.error('Error reloading config: path=%s', self.config_path)
            logging.error(traceback.format_exc())
            errors = True
        try:
            self.modules = mod_importer.get_modules(self.modules_dir)
            self.actions = mod_importer.process_modules(self.modules)
            self.add_builtins()
            logging.info('Loaded actions:')
            for a in self.actions:
                logging.info('> %r', a)
        except Exception, e:
            logging.error('Error reloading mods: path=%s', self.modules_dir)
            logging.error(traceback.format_exc())
            errors = True
        if not errors and not _init:
            self.run()

    def add_builtins(self):
        self.actions.insert(0, Action.from_func(BuiltinActions._reload))

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
        """The init function for this bot."""
        try:
            for chan in self.config.channels:
                if chan not in self.channels:
                    self.join(chan)
        except Exception, e:
            logging.error('Error joining channels.')
            logging.error(traceback.format_exc())

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
            logging.debug(line)
            self.parse(line)

    def parse(self, line):
        if self.parse_ping(line):
            return
        if self.parse_topic(line):
            return
        self.parse_other(line)

    def parse_ping(self, line):
        x = line.split(' ')
        if x and x[0] == 'PING':
            self.command.pong(' '.join(x[1:]))
            return True
        return False

    PARSE_TOPIC_REGEX = re.compile(r'^:(\S+) ([0-9]+) \S+ (#\S+) :(.*)$')
    def parse_topic(self, line):
        m = self.PARSE_TOPIC_REGEX.match(line)
        if not m:
            return
        sender = m.group(1)
        command = m.group(2)
        channel = m.group(3)
        newtopic = m.group(4)
        if sender.split('!')[0] == self.nick:
            return True
        if command == '332':
            logging.debug('topic for %s is %s', channel, newtopic)
            cb = self.pop_callback('TOPIC')
            logging.debug('cb = %s', str(cb))
            if cb:
                logging.debug('Calling callback.')
                cb(newtopic)
            return True
        # TODO error case.

    def wrapped(realself, info, nick):
        class Wrapper(object):
            def __init__(self):
                self.bot = realself
                self.sender = nick
                self.reply_to = nick
                self.in_channel = False
                self.channel = None
                if info[2].startswith('#'):
                    self.reply_to = info[2]
                    self.channel = info[2]
                    self.in_channel = True

            def from_owner(self):
                return nick == self.config.owner

            def from_admin(self):
                return self.from_owner() or nick in self.config.admins

            def reply(self, msg):
                return self.say('%s: %s' % (nick, msg))

            def say(self, msg):
                return self.bot.command.msg(self.reply_to, msg)

            def __getattr__(self, name):
                if name == 'reply':
                    return self.reply
                elif name == 'say':
                    return self.say
                return getattr(self.bot, name)
        return Wrapper()

    def parse_other(self, line):
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


class BuiltinActions(object):

    def _reload(bot, input):
        if not bot.from_admin():
            bot.reply('Not authorized.')
            return
        bot.reload()
        bot.reply('done.')
    _reload.rule = r'^.reload'
    _reload = staticmethod(_reload)
