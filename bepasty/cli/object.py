import argparse
import logging

from flask import Flask

from ..storage import create_storage


class Main(object):
    argparser = argparse.ArgumentParser(prog='bepasty-object')
    _subparsers = argparser.add_subparsers()
    argparser.add_argument('config', metavar='CONFIG')
    argparser.add_argument('names', metavar='NAME', nargs='+')

    def do_info(self, name, item, args):
        print name
        for key, value in sorted(item.meta.items()):
            print '  ', key, value

    _parser = _subparsers.add_parser('info', help='Display information about objects')
    _parser.set_defaults(func=do_info)

    def do_set(self, name, item, args):
        print name

        if args.flag_complete is not None:
            if args.flag_complete:
                print '  set complete'
            else:
                print '  set not complete'
            item.meta['complete'] = args.flag_complete

        if args.flag_unlocked is not None:
            if args.flag_unlocked:
                print '  set unlocked'
            else:
                print '  set not unlocked'
            item.meta['unlocked'] = args.flag_unlocked

    _parser = _subparsers.add_parser('set', help='Set flags on objects')
    _parser.set_defaults(func=do_set)
    _group = _parser.add_mutually_exclusive_group()
    _group.add_argument('-L', '--lock', dest='flag_unlocked', action='store_false', default=None)
    _group.add_argument('-l', '--unlock', dest='flag_unlocked', action='store_true', default=None)
    _group = _parser.add_mutually_exclusive_group()
    _group.add_argument('-C', '--uncomplete', dest='flag_complete', action='store_false', default=None)
    _group.add_argument('-c', '--complete', dest='flag_complete', action='store_true', default=None)

    def __call__(self):
        args = Main.argparser.parse_args()

        # Setup minimal application
        app = Flask(__name__)
        app.config.from_object('bepasty.config.Config')
        app.config.from_pyfile(args.config)
        storage = create_storage(app)

        # Setup application context
        with app.app_context():
            # Run all before request functions by hand
            for i in app.before_request_funcs.get(None, ()):
                i()

            for name in args.names:
                try:
                    with storage.openwrite(name) as item:
                        args.func(self, name, item, args)
                except Exception:
                    logging.exception('Failed to handle item %s', name)


if __name__ == '__main__':
    logging.basicConfig()
    Main()()
