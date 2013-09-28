import collections

from ctypes import (
        CDLL,
        c_char_p, c_void_p, c_int, c_uint64,
        POINTER,
        )

from . import errcheck

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
_rados_shutdown = _librados.rados_conf_read_file
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


class Rados(object):
    def __init__(self, cluster_name=None, client_name=None, config_file=None):
        self.cluster_name = cluster_name or 'ceph'
        self.client_name = client_name or 'client.admin'
        self.config_file = config_file

        self._context = c_void_p()

    def __enter__(self):
        if self._context:
            raise RuntimeError

        _rados_create2(self._context, self.cluster_name, self.client_name, 0)

        if self.config_file:
            _rados_conf_read_file(self._context, self.config_file)

        _rados_connect(self._context)

        return _RadosManager(self._context)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._context:
            raise RuntimeError

        _rados_shutdown(self._context)

        self._context = c_void_p()


class _RadosManager(object):
    def __init__(self, context):
        self._context = context

    def __getitem__(self, key):
        return RadosIoctx(self, key)

    def __delitem__(self, key):
        raise NotImplementedError

    def create_pool(self, key):
        raise NotImplementedError


class RadosIoctx(object):
    def __init__(self, rados, pool_name):
        self._context, self.pool_name = rados._context, pool_name

        self._io_context = c_void_p()

    def __enter__(self):
        if self._io_context:
            raise RuntimeError

        _rados_ioctx_create(self._context, self.pool_name, self._io_context)

        return _RadosIoctxManager(self._io_context)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._io_context:
            raise RuntimeError

        _rados_ioctx_destroy(self._io_context)

        self._io_context = c_void_p()


class _RadosIoctxManager(object):
    def __init__(self, io_context):
        self._io_context = io_context
