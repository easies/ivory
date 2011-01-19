import logging

TINYURL_URI = 'http://tinyurl.com/api-create.php?url=%s'


def shorten(bot, input):
    def short_callback(urlobj):
        logging.debug(str(dir(urlobj)))
        tiny_url = urlobj.read()
        logging.debug('read')
        if len(url) > len(tiny_url):
            bot.say(tiny_url)
#        urlobj.close()
    url = TINYURL_URI % input.group(1)
    bot.add_web(url, short_callback)
    logging.debug('shorten')
#shorten.rule = r'.*(https?://\S+)'


def fetch(bot, input):
    def fetch_callback(urlobj):
        l = len(urlobj.read())
        bot.say('done %d' % l)
    url = input.group(1)
    bot.add_web(url, fetch_callback)
fetch.rule = r'^.fetch:(https?://\S+)'
