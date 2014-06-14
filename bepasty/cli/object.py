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
        def _fix_meta(item, tnow):
            # compatibility support for bepasty 0.0.1 and pre-0.0.2
            # old items might have a 'timestamp' value which is not used any more
            # (superseded by 'timestamp-*') - delete it:
            item.meta.pop('timestamp', None)
            # old items might miss some of the timestamps we require,
            # just initialize them with the current time:
            for ts_key in ['timestamp-upload', 'timestamp-download', ]:
                if ts_key not in item.meta:
                    item.meta[ts_key] = tnow

        tnow = time.time()
        with storage.openwrite(name) as item:
            _fix_meta(item, tnow)
            file_name = item.meta['filename']
            file_size = item.meta['size']
            t_upload = item.meta['timestamp-upload']
            t_download = item.meta['timestamp-download']
            file_type = item.meta['type']
        purge = True
        if args.purge_age is not None:
            dt = args.purge_age * 24 * 3600  # n days since upload
            purge = purge and t_upload < tnow - dt
        if args.purge_inactivity is not None:
            dt = args.purge_inactivity * 24 * 3600  # n days inactivity (no download)
            purge = purge and t_download < tnow - dt
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
    _parser.add_argument('-I', '--inactivity', dest='purge_inactivity', type=int, default=None)
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
