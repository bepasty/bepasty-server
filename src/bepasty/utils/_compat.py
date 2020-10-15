# -*- coding: utf-8 -*-
# Copyright: 2014 Valentin Pratz <vp.pratz@yahoo.de>
# License: BSD 2-clause, see LICENSE for details.

import sys
import base64

__all__ = ['urljoin', 'urlparse']

PY2 = sys.version_info[0] == 2

if PY2:
    from urlparse import urlparse, urljoin

    range_type = xrange  # noqa: F821
    bytes_type = str
    iteritems = lambda d: d.iteritems()  # noqa: E731

    def base64_b64decode(data):
        return base64.b64decode(data)
else:
    from urllib.parse import urlparse, urljoin

    range_type = range
    bytes_type = bytes
    iteritems = lambda d: iter(d.items())  # noqa: E731

    def base64_b64decode(data):
        return base64.b64decode(data, validate=True)
