import sys

__all__ = ['urljoin', 'urlparse']

PY2 = sys.version_info[0] == 2

if PY2:
    from urlparse import urlparse, urljoin

    range_type = xrange  # noqa: F821
    bytes_type = str
    iteritems = lambda d: d.iteritems()  # noqa: E731
    from collections import MutableMapping  # noqa: F401
else:
    from urllib.parse import urlparse, urljoin

    range_type = range
    bytes_type = bytes
    iteritems = lambda d: iter(d.items())  # noqa: E731
    from collections.abc import MutableMapping  # noqa: F401
