import os
import sys
import re

from action import Action

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
                func.rule_comp = re.compile(getattr(func, 'rule'))
                actions.append(Action(func.rule_comp, func))
    return actions
