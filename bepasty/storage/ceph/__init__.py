# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import collections
import errno
import pickle

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
        """
        Open ioctx for data and meta-data storage.
        """
        g.ceph_ioctx_data = self.__cluster[self.pool_data]
        g.ceph_ioctx_data.open()

        if self.pool_data != self.pool_meta:
            g.ceph_ioctx_meta = self.__cluster[self.pool_meta]
            g.ceph_ioctx_meta.open()
        else:
            g.ceph_ioctx_meta = None

    def _teardown_request(self, exc):
        """
        Close ioctx for data and meta-data storage.
        """
        del g.ceph_ioctx_data
        del g.ceph_ioctx_meta

    def _objectname(self, name):
        return 'bepasty.' + name

    def create(self, name, size):
        objectname = self._objectname(name)
        rbd = Rbd(g.ceph_ioctx_data)
        data = rbd.create(objectname, size)
        meta = g.ceph_ioctx_data[objectname]
        return Item(data, meta)

    def open(self, name):
        # XXX: Read-only
        objectname = self._objectname(name)
        rbd = Rbd(g.ceph_ioctx_data)
        data = rbd[objectname]
        meta = g.ceph_ioctx_data[objectname]
        return Item(data, meta)

    def openwrite(self, name):
        objectname = self._objectname(name)
        rbd = Rbd(g.ceph_ioctx_data)
        data = rbd[objectname]
        meta = g.ceph_ioctx_data[objectname]
        return Item(data, meta)

    def remove(self, name):
        objectname = self._objectname(name)
        rbd = Rbd(g.ceph_ioctx_data)

        e_data = e_meta = None
        try:
            del rbd[objectname]
        except KeyError as e_data:
            pass
        try:
            del g.ceph_ioctx_data[objectname]
        except KeyError as e_meta:
            pass
        if e_data and e_meta:
            raise KeyError(name)

    def __iter__(self):
        # XXX rbd.list() not implemented yet
        # rbd = Rbd(g.ceph_ioctx_data)
        # names = [img[8:] for img in rbd.list()
        #          if img.startswith('bepasty.')]
        names = []
        for name in names:
            yield name


class Item(object):
    """
    Represents an open item.

    :ivar data: Open file-like object to data.
    """

    def __init__(self, rbd_data, object_meta):
        self.data = Data(rbd_data)
        self.meta = Meta(object_meta)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.data.close()
        self.meta.close()

    close = __exit__


class Data(object):
    """
    Data of item."
    """

    def __init__(self, rbd_data):
        self._rbd = rbd_data
        rbd_data.open()

    @property
    def size(self):
        return self._rbd.size

    def close(self):
        self._rbd.close()

    def read(self, size, offset):
        return self._rbd.read(size, offset)

    def write(self, data, offset):
        return self._rbd.write(data, offset)


class Meta(collections.MutableMapping):
    """
    Meta-data of item.
    """
    def __init__(self, object_meta):
        self._object = object_meta

        self._data = {}
        self._changed = True

        try:
            data = self._object.read(16 * 1024, 0)
            if data:
                self._data = pickle.loads(data)
                self._changed = False
        except OSError as e:
            if e.errno != 2:
                raise

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

    def write(self):
        if self._changed:
            self._write()
            self._changed = False

    def _write(self):
        buf = pickle.dumps(self._data)
        self._object.write_full(buf)
