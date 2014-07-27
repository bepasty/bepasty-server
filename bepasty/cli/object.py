# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

"""
bepasty-object commandline interface
"""

import os
import argparse
import logging
import time

from flask import Flask

from ..utils.hashing import compute_hash
from ..storage import create_storage
from ..utils.date_funcs import FOREVER


class Main(object):
    argparser = argparse.ArgumentParser(prog='bepasty-object')
    _subparsers = argparser.add_subparsers()
    argparser.add_argument('--config', dest='config', metavar='CONFIG', help='bepasty configuration file')
    argparser.add_argument('names', metavar='NAME', nargs='+')

    def do_migrate(self, storage, name, args):
        tnow = time.time()
        with storage.openwrite(name) as item:
            # compatibility support for bepasty 0.0.1 and pre-0.1.0
            # old items might have a 'timestamp' value which is not used any more
            # (superseded by 'timestamp-*') - delete it:
            item.meta.pop('timestamp', None)
            # old items might miss some of the timestamps we require,
            # just initialize them with the current time:
            for ts_key in ['timestamp-upload', 'timestamp-download', ]:
                if ts_key not in item.meta:
                    item.meta[ts_key] = tnow
            if 'locked' not in item.meta:
                unlocked = item.meta.pop('unlocked', None)
                if unlocked is not None:
                    locked = not unlocked
                else:
                    locked = False
                item.meta['locked'] = locked
            if 'complete' not in item.meta:
                item.meta['complete'] = True
            if 'filename' not in item.meta:
                item.meta['filename'] = 'missing'
            if 'type' not in item.meta:
                item.meta['type'] = 'application/octet-stream'
            if 'size' not in item.meta:
                item.meta['size'] = item.data.size
            if 'hash' not in item.meta:
                item.meta['hash'] = ''  # see do_consistency
            if 'timestamp-max-life' not in item.meta:
                item.meta['timestamp-max-life'] = FOREVER

    _parser = _subparsers.add_parser('migrate', help='Migrate metadata to current schema')
    _parser.set_defaults(func=do_migrate)

    def do_purge(self, storage, name, args):
        tnow = time.time()
        with storage.openwrite(name) as item:
            file_name = item.meta['filename']
            file_size = item.meta['size']
            t_upload = item.meta['timestamp-upload']
            t_download = item.meta['timestamp-download']
            file_type = item.meta['type']
            max_lifetime = item.meta.get('timestamp-max-life', FOREVER)
        purge = True  # be careful: we start from True, then AND the specified criteria
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
        if max_lifetime is not None:
            purge = purge and tnow > max_lifetime > 0
        if purge:
            print 'removing: %s (%s %dB %s)' % (name, file_name, file_size, file_type)
            if not args.purge_dry_run:
                storage.remove(name)

    _parser = _subparsers.add_parser('purge', help='Purge objects')
    _parser.set_defaults(func=do_purge)
    _parser.add_argument('-D', '--dry-run', dest='purge_dry_run', action='store_true',
                         help='do not remove anything, just display what would happen')
    _parser.add_argument('-A', '--age', dest='purge_age', type=int, default=None,
                         help='only remove if upload older than PURGE_AGE days')
    _parser.add_argument('-I', '--inactivity', dest='purge_inactivity', type=int, default=None,
                         help='only remove if latest download older than PURGE_INACTIVITY days')
    _parser.add_argument('-S', '--size', dest='purge_size', type=int, default=None,
                         help='only remove if file size > PURGE_SIZE MiB')
    _parser.add_argument('-T', '--type', dest='purge_type', default=None,
                         help='only remove if file mimetype starts with PURGE_TYPE')

    def do_consistency(self, storage, name, args):
        with storage.openwrite(name) as item:
            file_name = item.meta['filename']
            meta_size = item.meta['size']
            meta_type = item.meta['type']
            t_upload = item.meta['timestamp-upload']
            meta_hash = item.meta['hash']

            print 'checking: %s (%s %dB %s)' % (name, file_name, meta_size, meta_type)

            size = item.data.size
            size_consistent = size == meta_size
            if not size_consistent:
                print "Inconsistent file size: meta: %d file: %d" % (meta_size, size)
                if args.consistency_fix:
                    print "Writing computed file size into metadata..."
                    item.meta['size'] = size
                    size_consistent = True

            file_hash = compute_hash(item.data, size)
            hash_consistent = meta_hash == file_hash
            if not hash_consistent:
                if meta_hash:
                    print "Inconsistent hashes:"
                    print "meta: %s" % meta_hash
                    print "file: %s" % file_hash
                else:
                    # the upload code can not compute hashes for chunked uploads and thus stores an empty hash.
                    # we can fix that empty hash with the computed hash from the file we have in storage.
                    print "Empty hash in metadata."
                if args.consistency_fix or args.consistency_compute and not meta_hash:
                    print "Writing computed file hash into metadata..."
                    item.meta['hash'] = file_hash
                    hash_consistent = True

        if args.consistency_remove and not (size_consistent and hash_consistent):
            print 'REMOVING inconsistent file!'
            storage.remove(name)

    _parser = _subparsers.add_parser('consistency', help='Consistency-related functions')
    _parser.set_defaults(func=do_consistency)
    _parser.add_argument('-C', '--compute', dest='consistency_compute', action='store_true',
                         help='compute missing hashes and write into metadata')
    _parser.add_argument('-F', '--fix', dest='consistency_fix', action='store_true',
                         help='write computed hash/size into metadata')
    _parser.add_argument('-R', '--remove', dest='consistency_remove', action='store_true',
                         help='remove files with inconsistent hash/size')

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

            if args.flag_locked is not None:
                if args.flag_locked:
                    print '  set locked'
                else:
                    print '  set not locked'
                item.meta['locked'] = args.flag_locked

    _parser = _subparsers.add_parser('set', help='Set flags on objects')
    _parser.set_defaults(func=do_set)
    _group = _parser.add_mutually_exclusive_group()
    _group.add_argument('-L', '--lock', dest='flag_locked', action='store_true', default=None)
    _group.add_argument('-l', '--unlock', dest='flag_locked', action='store_false', default=None)
    _group = _parser.add_mutually_exclusive_group()
    _group.add_argument('-C', '--incomplete', dest='flag_complete', action='store_false', default=None)
    _group.add_argument('-c', '--complete', dest='flag_complete', action='store_true', default=None)

    def __call__(self):
        args = Main.argparser.parse_args()

        # Setup minimal application
        app = Flask(__name__)
        app.config.from_object('bepasty.config.Config')
        if os.environ.get('BEPASTY_CONFIG'):
            app.config.from_envvar('BEPASTY_CONFIG')
        if args.config is not None:
            cfg_path = os.path.abspath(args.config)
            app.config.from_pyfile(cfg_path)
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


def main():
    logging.basicConfig()
    Main()()


if __name__ == '__main__':
    main()
