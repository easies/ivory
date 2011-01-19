import os
import httplib
import threading
import re
import logging


class Web(threading.Thread):
    REGEX = re.compile(r'^http(s?)://([^/]+)(/?.*)')

    def __init__(self, url, *args, **kwargs):
        # Call Thread's __init__
        super(self.__class__, self).__init__(*args, **kwargs)
        self.ssl = False
        res = self.REGEX.match(url)
        if res:
            self.host = res.group(2)
            self.uri = res.group(3)
            self.ssl = False
            if res.group(1):
                self.ssl = True
        self.urlobj = None
        self.r, self.w = os.pipe()

    def fileno(self):
        """Returns the fileno to watch."""
        return self.r

    def get(self):
        """Get the Response object as returned by urllib2.urlopen."""
        os.close(self.r)
        return self.urlobj

    def notify(self):
        """Notify the poll/select by writing to the pipe."""
        # 'x' marks the spot.
        os.write(self.w, 'x')
        # Close the fd to guarantee a flush.
        os.close(self.w)

    def run(self):
        if not self.ssl:
            conn = httplib.HTTPConnection(self.host)
        else:
            conn = httplib.HTTPSConnection(self.host)
        conn.request('GET', self.uri)
        self.urlobj = conn.getresponse()
        self.notify()
