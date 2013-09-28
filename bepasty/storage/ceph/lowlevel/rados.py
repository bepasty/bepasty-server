from ctypes import (
        CDLL,
        c_char_p, c_size_t, c_void_p, c_char, c_int, c_long,
        c_ulong, create_string_buffer, c_uint64, c_ubyte,
        pointer, POINTER,
        )

from . import errcheck

_librados = CDLL('librados.so.2')

_rados_create2 = _librados.rados_create2
_rados_create2.restype = c_int
_rados_create2.errcheck = errcheck
_rados_create2.argtypes = POINTER(c_void_p), c_char_p, c_char_p, c_uint64

_rados_conf_read_file = _librados.rados_conf_read_file
_rados_conf_read_file.restype = c_int
_rados_conf_read_file.errcheck = errcheck
_rados_conf_read_file.argtypes = c_void_p, c_char_p

_rados_connect = _librados.rados_connect
_rados_connect.restype = c_int
_rados_connect.errcheck = errcheck
_rados_connect.argtypes = c_void_p,

_rados_shutdown = _librados.rados_conf_read_file
_rados_shutdown.restype = c_int
_rados_shutdown.errcheck = errcheck
_rados_shutdown.argtypes = c_void_p,


class Rados(object):
    def __init__(self, cluster_name=None, client_name=None, config_file=None):
        self.cluster_name = cluster_name or 'ceph'
        self.client_name = client_name or 'client.admin'
        self.config_file = config_file

        self.__context = c_void_p()

    def __enter__(self):
        if self.__context:
            raise RuntimeError

        _rados_create2(self.__context, self.cluster_name, self.client_name, 0)

        if self.config_file:
            _rados_conf_read_file(self.__context, self.config_file)

        _rados_connect(self.__context)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.__context:
            raise RuntimeError

        _rados_shutdown(self.__context)

        self.__context = None
