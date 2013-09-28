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
        self._destroy = destroy
        self._pointer = pointer
        self._extra = extra

    def destroy(self):
        print "destroy", self._destroy.__name__, self._pointer
        self._destroy(self._pointer)
        del self._pointer
        del self._extra

