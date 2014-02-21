# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import collections

from flask import request, abort
from werkzeug.exceptions import BadRequest


class ContentRange(collections.namedtuple('ContentRange', ('begin', 'end', 'complete'))):
    """
    Work with Content-Range headers.
    """
    __slots__ = ()

    @classmethod
    def parse(cls, content_range):
        """
        Parse Content-Range header.
        Format is "bytes 0-524287/2000000".
        """
        range_type, range_count = content_range.split(' ', 1)
        # There are no other types then "bytes"
        if range_type != 'bytes':
            raise BadRequest

        range_count, range_complete = range_count.split('/', 1)
        range_begin, range_end = range_count.split('-', 1)

        range_begin = int(range_begin)
        range_end = int(range_end)
        range_complete = int(range_complete)

        if range_begin <= range_end < range_complete:
            return ContentRange(range_begin, range_end, range_complete)

        raise BadRequest

    @classmethod
    def from_request(cls):
        """
        Read Content-Range from request and parse it
        """
        content_range = request.headers.get('Content-Range')
        if content_range is not None:
            return cls.parse(content_range)

    @property
    def is_complete(self):
        return self.complete == self.end + 1

    @property
    def size(self):
        return self.end - self.begin + 1
