import os
import pickle
import logging
import tempfile

from collections.abc import MutableMapping

logger = logging.getLogger(__name__)


def create_storage(app):
    # decouple Storage class from flask app
    storage_dir = app.config['STORAGE_FILESYSTEM_DIRECTORY']
    return Storage(storage_dir)


class Storage(object):
    """
    Filesystem storage - store meta and data into separate files in a directory.
    """
    def __init__(self, storage_dir):
        try:
            fd, fname = tempfile.mkstemp(dir=storage_dir)
        except OSError as e:
            logger.error("Could not write file in storage directory: %s\n %s", storage_dir, e)
            raise
        else:
            os.close(fd)
            os.remove(fname)
            self.directory = storage_dir

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
        return self._open(name, 'w+b')

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

    def __contains__(self, name):
        meta_filename = self._filename(name) + '.meta'
        return os.path.exists(meta_filename)


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


class Meta(MutableMapping):
    """
    Meta-data of item.
    """
    def __init__(self, file_meta):
        self._changed = False
        self._file = file_meta
        data = file_meta.read()
        if data:
            self._data = pickle.loads(data)
        else:
            # for empty input, we create a usable, empty Meta item,
            # but we do NOT set self._changed to True to avoid trying
            # to write to files opened in read-only mode.
            self._data = {}

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
        # Python 2.x only uses protocol 2, 3.x uses protocol 3 by default.
        # If we just use protocol 2, changing the Python version shouldn't
        # cause problems with existing pickles.
        pickle.dump(self._data, self._file, protocol=2)
        self._file.seek(0)
