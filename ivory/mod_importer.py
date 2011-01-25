import os
import sys
import imp
import logging
import traceback
from .action import Action


def get_modules(dirpath):
    mods = []
    for root, _, files, in os.walk(dirpath):
        for f in files:
            if f.endswith('.py') and not f.startswith('_'):
                try:
                    name = f.rsplit('.', 2)[0]
                    fullpath = os.path.join(root, f)
                    m = imp.load_source(name, fullpath)
                    mods.append(m)
                except Exception, e:
                    logging.error(traceback.format_exc())
        break
    return mods


def process_modules(mods):
    actions = []
    for m in mods:
        for name in dir(m):
            func = getattr(m, name)
            if hasattr(func, 'rule'):
                actions.append(Action(func.rule, func))
    return actions
