# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import collections
import errno

from ctypes import (
    CDLL,
    c_char_p, c_void_p, c_int, c_size_t, c_uint64,
    POINTER, create_string_buffer, string_at)

from . import errcheck, ContextWrapper

_librados = CDLL('librados.so.2')

# int rados_create2(rados_t *pcluster, const char *const clustername,
#                   const char * const name, uint64_t flags);
_rados_create2 = _librados.rados_create2
_rados_create2.restype = c_int
_rados_create2.errcheck = errcheck
_rados_create2.argtypes = POINTER(c_void_p), c_char_p, c_char_p, c_uint64

# int rados_conf_read_file(rados_t cluster, const char *path);
_rados_conf_read_file = _librados.rados_conf_read_file
_rados_conf_read_file.restype = c_int
_rados_conf_read_file.errcheck = errcheck
_rados_conf_read_file.argtypes = c_void_p, c_char_p

# int rados_connect(rados_t cluster);
_rados_connect = _librados.rados_connect
_rados_connect.restype = c_int
_rados_connect.errcheck = errcheck
_rados_connect.argtypes = c_void_p,

# void rados_shutdown(rados_t cluster);
_rados_shutdown = _librados.rados_shutdown
_rados_shutdown.restype = None
_rados_shutdown.argtypes = c_void_p,

# int rados_ioctx_create(rados_t cluster, const char *pool_name, rados_ioctx_t *ioctx);
_rados_ioctx_create = _librados.rados_ioctx_create
_rados_ioctx_create.restype = c_int
_rados_ioctx_create.errcheck = errcheck
_rados_ioctx_create.argtypes = c_void_p, c_char_p, POINTER(c_void_p)

# void rados_ioctx_destroy(rados_ioctx_t io);
_rados_ioctx_destroy = _librados.rados_ioctx_destroy
_rados_ioctx_destroy.restype = None
_rados_ioctx_destroy.argtypes = c_void_p,

# int rados_write(rados_ioctx_t io, const char *oid, const char *buf, size_t len, uint64_t off);
_rados_write = _librados.rados_write
_rados_write.restype = c_int
_rados_write.errcheck = errcheck
_rados_write.argtypes = c_void_p, c_char_p, c_char_p, c_size_t, c_uint64

# int rados_write_full(rados_ioctx_t io, const char *oid, const char *buf, size_t len);
_rados_write_full = _librados.rados_write_full
_rados_write_full.restype = c_int
_rados_write_full.errcheck = errcheck
_rados_write_full.argtypes = c_void_p, c_char_p, c_char_p, c_size_t

# int rados_read(rados_ioctx_t io, const char *oid, char *buf, size_t len, uint64_t off);
_rados_read = _librados.rados_read
_rados_read.restype = c_int
_rados_read.errcheck = errcheck
_rados_read.argtypes = c_void_p, c_char_p, c_char_p, c_size_t, c_uint64

# int rados_remove(rados_ioctx_t io, const char *oid);
_rados_remove = _librados.rados_remove
_rados_remove.restype = c_int
_rados_remove.errcheck = errcheck
_rados_remove.argtypes = c_void_p, c_char_p


class Rados(object):
    def __init__(self, cluster_name=None, client_name=None, config_file=None):
        self.cluster_name = cluster_name or 'ceph'
        self.client_name = client_name or 'client.admin'
        self.config_file = config_file

        self._context = None

    def __enter__(self):
        if self._context:
            raise RuntimeError

        context = c_void_p()

        _rados_create2(context, self.cluster_name, self.client_name, 0)

        if self.config_file:
            _rados_conf_read_file(context, self.config_file)

        _rados_connect(context)

        self._context = ContextWrapper(_rados_shutdown, context)

        return self

    def __exit__(self, *exc):
        self._context.destroy()
        self._context = None

    open = __enter__
    close = __exit__

    def __getitem__(self, key):
        return RadosIoctx(self, key)

    def __delitem__(self, key):
        raise NotImplementedError

    def create_pool(self, key):
        raise NotImplementedError


class RadosIoctx(object):
    def __init__(self, rados, pool_name):
        self._context, self.pool_name = rados._context, pool_name

        self._io_context = None

    def __enter__(self):
        if self._io_context:
            raise RuntimeError

        context = c_void_p()

        _rados_ioctx_create(self._context.pointer, self.pool_name, context)

        self._io_context = ContextWrapper(_rados_ioctx_destroy, context, self._context)

        return self

    def __exit__(self, *exc):
        self._io_context.destroy()
        self._io_context = None

    open = __enter__
    close = __exit__

    def __getitem__(self, name):
        return RadosObject(self._io_context, name)

    def __delitem__(self, name):
        try:
            _rados_remove(self._io_context.pointer, name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise KeyError(name)
            raise


class RadosObject(object):
    def __init__(self, io_context, name):
        self._io_context, self.name = io_context, name

    def read(self, size, offset):
        buf = create_string_buffer(size)
        ret = _rados_read(self._io_context.pointer, self.name, buf, size, offset)
        return string_at(buf, ret)

    def write(self, buf, offset):
        return _rados_write(self._io_context.pointer, self.name, buf, len(buf), offset)

    def write_full(self, buf):
        return _rados_write_full(self._io_context.pointer, self.name, buf, len(buf))
