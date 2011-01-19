import logging
from skynet import SkyNet
from bot import Bot
import sys
import gflags

gflags.DEFINE_string('nick', 'ivory', 'The bot\'s nickname.')
gflags.DEFINE_string('name', 'Bot Bot Bot', 'The bot\'s name.')
gflags.DEFINE_string('host', None, 'The host to connect to.')
gflags.DEFINE_integer('port', 6667, 'The port.')
gflags.DEFINE_string('moddir', './modules', 'The module directory.')
FLAGS = gflags.FLAGS

LOGFORMAT = '%(asctime)s %(filename)s %(lineno)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT)


def main():
    FLAGS(sys.argv)
    if not FLAGS.host:
        sys.stderr.write('Please specify a host.')
    skynet = SkyNet()
    b = Bot(skynet=skynet, name=FLAGS.name, nick=FLAGS.nick,
        network=FLAGS.host, port=FLAGS.port, modules_dir=FLAGS.moddir)
    skynet.add_bot(b)
    b.connect()
    b.run()
    try:
        skynet.main()
    except Exception, e:
        logging.error(e)
        skynet.die()


if __name__ == '__main__':
    main()
