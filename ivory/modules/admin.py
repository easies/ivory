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


def add_topic(bot, input):
    if not bot.in_channel:
        return
    t = input.group(1).strip()
    def cb(old):
        bot.command.topic(bot.channel, ' | '.join([old, t]))
    bot.command.topic(bot.channel, receiver=cb)
add_topic.rule = r'^.topic-append (.+)$'
