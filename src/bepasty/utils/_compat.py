# -*- coding: utf-8 -*-
# Copyright: 2014 Valentin Pratz <vp.pratz@yahoo.de>
# License: BSD 2-clause, see LICENSE for details.

import sys

__all__ = ['urljoin', 'urlparse']

PY2 = sys.version_info[0] == 2

if PY2:
    from urlparse import urlparse, urljoin

    range_type = xrange  # noqa: F821
    iteritems = lambda d: d.iteritems()  # noqa: E731
else:
    from urllib.parse import urlparse, urljoin

    range_type = range
    iteritems = lambda d: iter(d.items())  # noqa: E731
