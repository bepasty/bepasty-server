# -*- coding: utf-8 -*-
# Copyright: 2014 Valentin Pratz <vp.pratz@yahoo.de>
# License: BSD 2-clause, see LICENSE for details.

import sys

PY2 = sys.version_info[0] == 2
_identity = lambda x: x


if not PY2:
    range_type = range

    from urllib.parse import urlparse, urljoin
    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())
else:
    range_type = xrange

    from urlparse import urlparse, urljoin
    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()
