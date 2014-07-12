# Copyright: 2014 Dennis Schmalacker <github@progde.de>
# License: BSD 2-clause, see LICENSE for details.

import re
import time

from flask import abort, current_app

from .decorators import async
from .hashing import compute_hash, hash_new

# we limit to 250 characters as we do not want to accept arbitrarily long
# filenames. other than that, there is no specific reason we could not
# also take more (or less).
MAX_FILENAME_LENGTH = 250


class Upload(object):
    _filename_re = re.compile(r'[^a-zA-Z0-9 \*+:;.,_-]+')
    _type_re = re.compile(r'[^a-zA-Z0-9/+.-]+')

    @classmethod
    def filter_size(cls, i):
        """
        Filter size.
        Check for advertised size.
        """
        i = int(i)
        if i >= 4 * 1024 * 1024 * 1024:  # 4 GiB
            abort(413)
        return i

    @classmethod
    def filter_filename(cls, filename, storage_name, content_type):
        """
        Filter filename.
        Only allow some basic characters and shorten to 50 characters.
        """
        # Make up filename if we don't have one
        if not filename:
            # note: stdlib mimetypes.guess_extension is total crap
            if content_type.startswith("text/"):
                ext = ".txt"
            else:
                ext = ".bin"
            filename = storage_name + ext
        return cls._filename_re.sub('', filename)[:MAX_FILENAME_LENGTH]

    @classmethod
    def filter_type(cls, i):
        """
        Filter Content-Type
        Only allow some basic characters and shorten to 50 characters.
        """
        if not i:
            return 'application/octet-stream'
        return cls._type_re.sub('', i)[:50]

    @classmethod
    def meta_new(cls, item, input_size, input_filename, input_type, storage_name):
        item.meta['filename'] = cls.filter_filename(input_filename, storage_name, input_type)
        item.meta['size'] = cls.filter_size(input_size)
        item.meta['type'] = cls.filter_type(input_type)
        item.meta['timestamp-upload'] = int(time.time())
        item.meta['timestamp-download'] = 0
        item.meta['locked'] = current_app.config['UPLOAD_LOCKED']
        item.meta['complete'] = False
        item.meta['hash'] = ''

    @classmethod
    def meta_complete(cls, item, file_hash):
        item.meta['complete'] = True
        item.meta['hash'] = file_hash

    @staticmethod
    def data(item, f, size_input, offset=0):
        """
        Copy data from temp file into storage.
        """
        read_length = 16 * 1024
        size_written = 0
        hasher = hash_new()

        while True:
            read_length = min(read_length, size_input)
            if size_input == 0:
                break

            buf = f.read(read_length)
            if not buf:
                # Should not happen, we already checked the size
                raise RuntimeError

            item.data.write(buf, offset + size_written)
            hasher.update(buf)

            len_buf = len(buf)
            size_written += len_buf
            size_input -= len_buf

        return size_written, hasher.hexdigest()


@async
def background_compute_hash(storage, name):
        with storage.openwrite(name) as item:
            size = item.meta['size']
            file_hash = compute_hash(item.data, size)
            item.meta['hash'] = file_hash
