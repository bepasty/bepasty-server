# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import collections

from flask import g

from .lowlevel.rados import Rados
from .lowlevel.rbd import Rbd


class Storage(object):
    def __init__(self, app):
        config_file = app.config['STORAGE_CEPH_CONFIG_FILE']
        self.pool_data = app.config['STORAGE_CEPH_POOL_DATA']
        self.pool_meta = app.config['STORAGE_CEPH_POOL_META']

        self.__cluster = Rados(config_file=config_file)
        self.__cluster.open()

        app.before_request(self._before_request)
        app.teardown_request(self._teardown_request)
        app.storage = self

    def _before_request(self):
        g.ceph_ioctx_data = self.__cluster[self.pool_data]
        g.ceph_ioctx_data.open()

        if self.pool_data != self.pool_meta:
            g.ceph_ioctx_meta = self.__cluster[self.pool_meta]
            g.ceph_ioctx_meta.open()
        else:
            g.ceph_ioctx_meta = None

    def _teardown_request(self, exc):
        del g.ceph_ioctx_data
        del g.ceph_ioctx_meta

    def create(self, name, size):
        rbd = Rbd(g.ceph_ioctx_data)
        image = rbd.create(name, size)
        return Item(name, image, g.ceph_ioctx_meta)

    def open(self, name):
        # XXX: Read-only
        rdb = Rdb(g.ceph_ioctx_data)
        image = rbd[name]
        return Item(name, image, g.ceph_ioctx_meta)

    def openwrite(self, name):
        rdb = Rdb(g.ceph_ioctx_data)
        image = rbd[name]
        return Item(name, image, g.ceph_ioctx_meta)

    def destroy(self, name):
        raise NotImplementedError


class Item(object):
    """
    Represents an open item.

    :ivar data: Open file-like object to data.
    """

    def __init__(self, name, rbd_data, ioctx_meta):
        self.data = Data(rbd_data)
        self.meta = Meta(name, ioctx_meta)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.data.close()
        self.meta.close()


class Data(object):
    """
    Data of item."
    """

    def __init__(self, rbd_data):
        self._rbd = rbd_data
        rbd_data.open()

    @property
    def size(self):
        return self._rbd.size()

    def close(self):
        self._rbd.close()

    def read(self, offset, length):
        raise NotImplementedError

    def write(self, data, offset):
        raise NotImplementedError


class Meta(collections.MutableMapping):
    """
    Meta-data of item.
    """
    def __init__(self, name, ioctx_meta):
        self._ioctx = ioctx_meta

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
        self._ioctx.close()

    def write(self):
        pass

    def _write(self):
        self._file.seek(0)
        pickle.dump(self._data, self._file)
        self._file.seek(0)

