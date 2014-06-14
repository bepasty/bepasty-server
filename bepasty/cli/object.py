import argparse
import logging
import time

from flask import Flask

from ..storage import create_storage


class Main(object):
    argparser = argparse.ArgumentParser(prog='bepasty-object')
    _subparsers = argparser.add_subparsers()
    argparser.add_argument('config', metavar='CONFIG')
    argparser.add_argument('names', metavar='NAME', nargs='+')

    def do_purge(self, storage, name, args):
        with storage.open(name) as item:
            file_name = item.meta['filename']
            file_size = item.meta['size']
            t_upload = item.meta['timestamp-upload']
            file_type = item.meta['type']
        purge = True
        if args.purge_age is not None:
            dt = args.purge_age * 24 * 3600  # age in days
            tnow = time.time()
            purge = purge and t_upload < tnow - dt
        if args.purge_size is not None:
            max_size = args.purge_size * 1024 * 1024  # size in MiB
            purge = purge and file_size > max_size
        if args.purge_type is not None:
            purge = purge and file_type.startswith(args.purge_type)
        if purge:
            print 'removing: %s (%s %dB %s)' % (name, file_name, file_size, file_type)
            if not args.purge_dry_run:
                storage.remove(name)

    _parser = _subparsers.add_parser('purge', help='Purge objects')
    _parser.set_defaults(func=do_purge)
    _parser.add_argument('-S', '--size', dest='purge_size', type=int, default=None)
    _parser.add_argument('-A', '--age', dest='purge_age', type=int, default=None)
    _parser.add_argument('-T', '--type', dest='purge_type', default=None)
    _parser.add_argument('-D', '--dry-run', dest='purge_dry_run', action='store_true')

    def do_info(self, storage, name, args):
        with storage.open(name) as item:
            print name
            for key, value in sorted(item.meta.items()):
                print '  ', key, value

    _parser = _subparsers.add_parser('info', help='Display information about objects')
    _parser.set_defaults(func=do_info)

    def do_set(self, storage, name, args):
        with storage.openwrite(name) as item:
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

            if len(args.names) == 1 and args.names[0] == '*':
                names = list(storage)
            else:
                names = args.names
            for name in names:
                try:
                    args.func(self, storage, name, args)
                except Exception:
                    logging.exception('Failed to handle item %s', name)


if __name__ == '__main__':
    logging.basicConfig()
    Main()()
