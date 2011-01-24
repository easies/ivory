import os
import sys
import imp
import logging
import traceback
from .action import Action

def get_modules(module):
    mods = []
    for root, _, files, in os.walk(os.path.dirname(module.__file__)):
        for f in files:
            if f.endswith('.py') and not f.startswith('_'):
                name = f.split('.', 2)[0]
                __import__('%s.%s' % (module.__name__, name))
                mods.append(getattr(module, name))
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


def load_module(path):
    name = os.path.basename(path)
    directory = os.path.dirname(path)
    fp = None
    try:
        fp, path, desc = imp.find_module(name, [directory])
        return imp.load_module(name, fp, path, desc)
    finally:
        if fp:
            fp.close()
