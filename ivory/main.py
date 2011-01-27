import os
import sys
import logging
import gflags
from .skynet import SkyNet
from .bot import Bot
from .conf import Config

gflags.DEFINE_string('conf', '~/.ivory/default.py', 'The config module.')
gflags.DEFINE_boolean('init', False, '''Initialize ivory by creating a
    default config file.''')
FLAGS = gflags.FLAGS

LOGFORMAT = '%(asctime)s %(filename)s %(lineno)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT)


def main():
    FLAGS(sys.argv)
    if FLAGS.init:
        import gendefault
        mdir = os.path.join(os.path.dirname(gendefault.__file__), 'modules')
        gendefault.main(FLAGS.conf, mdir)
        return
    config = Config(FLAGS.conf)
    skynet = SkyNet()
    b = Bot(skynet=skynet, name=config.name, nick=config.nick,
        network=config.host, port=config.port, modules_dir=config.modules,
        config_path=FLAGS.conf)
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
