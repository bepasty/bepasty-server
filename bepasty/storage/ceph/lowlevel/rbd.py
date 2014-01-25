# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import collections
import errno

from ctypes import (
    CDLL,
    c_char_p, c_void_p, c_int, c_size_t, c_ssize_t, c_uint64,
    POINTER, create_string_buffer, string_at)

from . import errcheck, ContextWrapper

_librbd = CDLL('librbd.so.1')

# int rbd_create3(rados_ioctx_t io, const char *name, uint64_t size,
#                 uint64_t features, int *order,
#                 uint64_t stripe_unit, uint64_t stripe_count);
_rbd_create3 = _librbd.rbd_create3
_rbd_create3.restype = c_int
_rbd_create3.errcheck = errcheck
_rbd_create3.argtypes = c_void_p, c_char_p, c_uint64, c_uint64, POINTER(c_int), c_uint64, c_uint64

# int rbd_remove(rados_ioctx_t io, const char *name);
_rbd_remove = _librbd.rbd_remove
_rbd_remove.restype = c_int
_rbd_remove.errcheck = errcheck
_rbd_remove.argtypes = c_void_p, c_char_p

# int rbd_open(rados_ioctx_t io, const char *name, rbd_image_t *image,
#              const char *snap_name);
_rbd_open = _librbd.rbd_open
_rbd_open.restype = c_int
_rbd_open.errcheck = errcheck
_rbd_open.argtypes = c_void_p, c_char_p, POINTER(c_void_p), c_char_p

# int rbd_close(rbd_image_t image);
_rbd_close = _librbd.rbd_close
_rbd_close.restype = c_int
_rbd_close.errcheck = errcheck
_rbd_close.argtypes = c_void_p,

# int rbd_get_size(rbd_image_t image, uint64_t *size);
_rbd_get_size = _librbd.rbd_get_size
_rbd_get_size.restype = c_int
_rbd_get_size.errcheck = errcheck
_rbd_get_size.argtypes = c_void_p, POINTER(c_uint64)

# ssize_t rbd_read(rbd_image_t image, uint64_t ofs, size_t len, char *buf);
_rbd_read = _librbd.rbd_read
_rbd_read.restype = c_ssize_t
_rbd_read.errcheck = errcheck
_rbd_read.argtypes = c_void_p, c_uint64, c_size_t, c_char_p

# ssize_t rbd_write(rbd_image_t image, uint64_t ofs, size_t len, const char *buf);
_rbd_write = _librbd.rbd_write
_rbd_write.restype = c_ssize_t
_rbd_write.errcheck = errcheck
_rbd_write.argtypes = c_void_p, c_uint64, c_size_t, c_char_p


class Rbd(object):
    def __init__(self, pool):
        self.pool = pool

    def __getitem__(self, name):
        return _RbdImage(self.pool._io_context, name)

    def __delitem__(self, name):
        try:
            _rbd_remove(self.pool._io_context.pointer, name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise KeyError(name)
            raise

    def create(self, name, size, features=0,
               order=0, stripe_unit=0, stripe_count=0):
        order_c = c_int(order)
        _rbd_create3(self.pool._io_context.pointer, name, size, features, order_c, stripe_unit, stripe_count)
        return self[name]


class _RbdImage(object):
    def __init__(self, io_context, image_name):
        self._io_context, self.image_name = io_context, image_name

        self._image_context = None

    def __enter__(self):
        if self._image_context:
            raise RuntimeError

        context = c_void_p()

        _rbd_open(self._io_context.pointer, self.image_name, context, None)

        self._image_context = ContextWrapper(_rbd_close, context, self._io_context)

        return self

    def __exit__(self, *exc):
        self._image_context.destroy()
        self._image_context = None

    open = __enter__
    close = __exit__

    @property
    def size(self):
        size = c_uint64()
        _rbd_get_size(self._image_context.pointer, size)
        return size.value

    def read(self, size, offset):
        buf = create_string_buffer(size)
        ret = _rbd_read(self._image_context.pointer, offset, size, buf)
        return string_at(buf, ret)

    def write(self, buf, offset):
        return _rbd_write(self._image_context.pointer, offset, len(buf), buf)
