import logging


def join(bot, input):
    channel = input.group(1)
    logging.info('Trying to join %s', channel)
    bot.join(channel)
join.rule = r'^.join (#\S+)'


def _reload(bot, input):
    bot.reload()
    bot.reply('done.')
_reload.rule = r'^.reload'
