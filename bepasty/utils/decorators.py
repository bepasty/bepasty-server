# Copyright: 2014 Thomas Waldmann <tw@waldmann-edv.de>
# License: BSD 2-clause, see LICENSE for details.

from threading import Thread


def async(func):
    """
    decorator to run a function asynchronously (in a thread)

    be careful: do not access flask threadlocals in f!
    """
    def wrapper(*args, **kwargs):
        t = Thread(target=func, args=args, kwargs=kwargs)
        t.start()
    return wrapper
