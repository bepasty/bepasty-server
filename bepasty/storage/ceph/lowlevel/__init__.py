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

