"""
The config module.
"""
import os
import logging
import traceback
import mod_importer


class Config(object):

    def __init__(self, path):
        x = os.path.expanduser(path)
        self._path = os.path.abspath(os.path.normpath(x))
        self._path = self._path.rstrip('.py')
        self._mod = None
        self._config = {}
        self._reload()

    def _reload(self):
        try:
            self._mod = mod_importer.load_module(self._path)
            self._save()
        except Exception, e:
            logging.error('Error in reloading config: path=%s', self._path)
            logging.error(traceback.format_exc())

    def _save(self):
        self._config = {}
        for name in dir(self._mod):
            if name.startswith('_'):
                continue
            self._config[name] = getattr(self._mod, name)

    def __getattr__(self, name):
        try:
            return self._config[name]
        except:
            return super(self.__class__, self).__getattribute__(name)
