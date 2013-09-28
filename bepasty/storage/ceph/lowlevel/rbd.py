# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import collections

from ctypes import (
        CDLL,
        c_char_p, c_void_p, c_int, c_uint64,
        POINTER,
        )

from . import errcheck

_librbd = CDLL('librbd.so.1')

# int rbd_create3(rados_ioctx_t io, const char *name, uint64_t size,
#                 uint64_t features, int *order,
#                 uint64_t stripe_unit, uint64_t stripe_count);
_rbd_create3 = _librbd.rbd_create3
_rbd_create3.restype = c_int
_rbd_create3.errcheck = errcheck
_rbd_create3.argtypes = c_void_p, c_char_p, c_uint64, c_uint64, POINTER(c_int), c_uint64, c_uint64

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


class Rbd(object):
    def __init__(self, pool):
        self.pool = pool

    def __getitem__(self, name):
        return _RbdImage(self.pool._io_context, name)

    def __delitem__(self, name):
        raise NotImplementedError

    def create(self, name, size, features=0,
               order=0, stripe_unit=0, stripe_count=0):
        order_c = c_int(order)
        _rbd_create3(self.pool._io_context, name, size, features, order_c, stripe_unit, stripe_count)
        return self[name]


class _RbdImage(object):
    def __init__(self, io_context, image_name):
        self._io_context, self.image_name = io_context, image_name

        self._image = c_void_p()

    def __enter__(self):
        if self._image:
            raise RuntimeError

        _rbd_open(self._io_context, self.image_name, self._image, None)

        return _RbdImageManager(self._image)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._image:
            raise RuntimeError

        _rbd_close(self._image)

        self._image = c_void_p()


class _RbdImageManager(object):
    def __init__(self, image):
        self._image = image

    @property
    def size(self):
        size = c_uint64()
        _rbd_get_size(self._image, size)
        return size.value


