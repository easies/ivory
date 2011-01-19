import logging


class Action(object):

    def __init__(self, rule, func):
        self.rule = rule
        self.func = func

    def __call__(self, wrapped_bot, line):
        match = self.rule.search(line)
        if match is not None:
            logging.debug('Calling %s' % self.func.__name__)
            self.func(wrapped_bot(), match)
            logging.debug('Done calling %s.' % self.func.__name__)
            return True
        return False
