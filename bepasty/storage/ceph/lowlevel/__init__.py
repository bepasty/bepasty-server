# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import os


def errcheck(result, func, *arguments):
    if result is None:
        pass
    elif result < 0:
        try:
            mesg = os.strerror(-result)
        except ValueError:
            mesg = 'Unknown error'
        raise OSError(-result, mesg)
    return result


class ContextWrapper(object):
    """
    Wrap pointer and corresponding destroy function.
    Used as reference counting for native pointer.
    """

    def __init__(self, destroy, pointer, *extra):
        self.__destroy = destroy
        self.__pointer = pointer
        self.__extra = extra

    def __del__(self):
        if self.__pointer is not None:
            self.__destroy(self.__pointer)
        self.__pointer = self.__extra = None

    destroy = __del__

    @property
    def pointer(self):
        p = self.__pointer
        if p is None:
            raise RuntimeError
        return p
