# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import collections
import os
import pickle
import logging
import tempfile

logger = logging.getLogger(__name__)


class Storage(object):
    """
    Filesystem storage - store meta and data into separate files in a directory.
    """
    def __init__(self, app):
        storage_dir = app.config['STORAGE_FILESYSTEM_DIRECTORY']
        try:
            fd, fname = tempfile.mkstemp(dir=storage_dir)
        except OSError as e:
            logger.error("Could not write file in storage directory: %s\n %s", storage_dir, e)
            raise
        else:
            os.close(fd)
            os.remove(fname)
            self.directory = storage_dir
            app.storage = self

    def _filename(self, name):
        if '/' in name:
            raise RuntimeError
        return os.path.join(self.directory, name)

    def _open(self, name, mode):
        basefilename = self._filename(name)
        file_data = open(basefilename + '.data', mode)
        file_meta = open(basefilename + '.meta', mode)
        return Item(file_data, file_meta)

    def create(self, name, size):
        return self._open(name, 'w+bx')

    def open(self, name):
        return self._open(name, 'rb')

    def openwrite(self, name):
        return self._open(name, 'r+b')

    def remove(self, name):
        basefilename = self._filename(name)
        file_data = basefilename + '.data'
        file_meta = basefilename + '.meta'
        try:
            os.remove(file_data)
        except OSError as e:
            logger.error("Could not delete file: %s\n %s" % (file_data, str(e)))
            raise
        try:
            os.remove(file_meta)
        except OSError as e:
            logger.error("Could not delete file: %s\n %s" % (file_meta, str(e)))
            raise

    def __iter__(self):
        names = [fn[:-5] for fn in os.listdir(self.directory)
                 if fn.endswith('.meta')]
        for name in names:
            yield name


class Item(object):
    """
    Represents an open item.

    :ivar data: Open file-like object to data.
    """
    def __init__(self, file_data, file_meta):
        """
        :param file_data: Open file-like object to data file.
        :param file_meta: Open file-like object to meta file.
        """
        self.data = Data(file_data)
        self.meta = Meta(file_meta)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.data.close()
        self.meta.close()

    close = __exit__


class Data(object):
    """
    Data of item.
    """
    def __init__(self, file_data):
        self._file = file_data

    @property
    def size(self):
        self._file.seek(0, os.SEEK_END)
        return self._file.tell()

    def close(self):
        self._file.close()

    def read(self, size, offset):
        self._file.seek(offset)
        return self._file.read(size)

    def write(self, data, offset):
        self._file.seek(offset)
        return self._file.write(data)


class Meta(collections.MutableMapping):
    """
    Meta-data of item.
    """
    def __init__(self, file_meta):
        self._file = file_meta
        data = file_meta.read()
        if data:
            self._data = pickle.loads(data)
            self._changed = False
        else:
            self._data = {}
            self._changed = True

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._changed = True

    def __delitem__(self, key):
        del self._data[key]
        self._changed = True

    def close(self):
        self.write()
        self._file.close()

    def write(self):
        if self._changed:
            self._write()
            self._changed = False

    def _write(self):
        self._file.seek(0)
        pickle.dump(self._data, self._file)
        self._file.seek(0)
