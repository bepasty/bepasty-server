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


class ContextWrapper(object):
    """
    Wrap pointer and corresponding destroy function.
    Used as reference counting for native pointer.
    """

    def __init__(self, destroy, pointer, *extra):
        self.__destroy = destroy
        self.__pointer = pointer
        self.__extra = extra

    def destroy(self):
        print "destroy", self.__destroy.__name__, self.__pointer
        self.__destroy(self.__pointer)
        self.__pointer = None
        del self.__extra

    @property
    def pointer(self):
        p = self.__pointer
        if p is None:
            raise RuntimeError
        return p

