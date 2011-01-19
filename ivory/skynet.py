import select
import logging
import functools
from web import Web


class SkyNet(object):
    TYPES = {
        'BOT': (1, select.EPOLLIN),
        'WEB': (2, select.EPOLLIN),
    }

    def __init__(self):
        self.socks = {}
        self.poller = select.epoll()

    def add_bot(self, bot):
        self.add(bot, 'BOT', bot.handle)

    def add_web(self, url, callback):
        @functools.wraps(callback)
        def new_callback(obj):
            return callback(obj.get())
        # A Web is a Thread.
        w = Web(url)
        w.start()
        self.add(w, 'WEB', new_callback)

    def add(self, obj, obj_type, callback):
        typ, event = SkyNet.TYPES[obj_type]
        self.socks[obj.fileno()] = (typ, obj, callback)
        self.poller.register(obj.fileno(), event)

    def remove_bot(self, bot):
        fileno = bot.sock.fileno()
        if fileno in self.socks.keys():
            self.socks.pop(fileno)
            self.poller.unregister(fileno)

    def remove(self, fd):
        typ, obj, callback = self.socks[fd]
        self.socks.pop(fd)
        self.poller.unregister(fd)

    def die(self):
        for typ, obj in self.socks.iteritems():
            if typ == 'BOT':
                obj.die()
            elif typ == 'WEB':
                obj.close()

    def main(self):
        while True:
            for fd, event in self.poller.poll():
                typ, obj, callback = self.socks[fd]
                try:
                    logging.debug(str(obj))
                    callback(obj)
                    logging.debug('%s called' % callback.__name__)
                except Exception, e:
                    logging.error(str(e))
                if typ == 2:
                    logging.debug('unregistering web.')
                    self.remove(obj.fileno())
