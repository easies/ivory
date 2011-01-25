import logging
import re


class Action(object):

    @classmethod
    def from_func(cls, func):
        return cls(func.rule, func)

    def __init__(self, rule, func):
        self.rule = re.compile(rule)
        self.rule_orig = rule
        self.func = func

    def __call__(self, wrapped_bot, line):
        match = self.rule.search(line)
        if match is not None:
            logging.debug('Calling %s' % self.func.__name__)
            self.func(wrapped_bot(), match)
            logging.debug('Done calling %s.' % self.func.__name__)
            return True
        return False

    def __str__(self):
        return '<Action %s "%s">' % (self.func.__name__, self.rule_orig)

    __repr__ = __str__
