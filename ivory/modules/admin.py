import logging


def join(bot, input):
    if not bot.from_admin():
        bot.reply('Not authorized.')
        return
    channel = input.group(1)
    logging.info('Trying to join %s', channel)
    bot.join(channel)
join.rule = r'^.join (#\S+)'


def part(bot, input):
    if not bot.from_admin():
        bot.reply('Not authorized.')
    bot.command.part([])
part.rule = r'^.part (#\S+)'
