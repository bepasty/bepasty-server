__all__ = ['urljoin', 'urlparse']

from urllib.parse import urlparse, urljoin

range_type = range
bytes_type = bytes
iteritems = lambda d: iter(d.items())  # noqa: E731
from collections.abc import MutableMapping  # noqa: F401
