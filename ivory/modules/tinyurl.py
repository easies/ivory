import logging

TINYURL_URI = 'http://tinyurl.com/api-create.php?url=%s'


def shorten(bot, input):
    orig_url = input.group(1)
    def short_callback(urlobj):
        tiny_url = urlobj.read()
        logging.debug('new: %s', tiny_url)
        logging.debug('orig: %s', orig_url)
        if len(orig_url) > len(tiny_url):
            bot.say(tiny_url)
    bot.add_web(TINYURL_URI % orig_url, short_callback)
    logging.debug('shorten')
shorten.rule = r'(https?://\S+)'


def fetch(bot, input):
    def fetch_callback(urlobj):
        l = len(urlobj.read())
        bot.say('done %d' % l)
    url = input.group(1)
    bot.add_web(url, fetch_callback)
fetch.rule = r'^.fetch:(https?://\S+)'
