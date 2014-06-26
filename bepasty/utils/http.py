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


class DownloadRange(collections.namedtuple('DownloadRange', ('begin', 'end'))):
    """
    Work with Content-Range headers.
    """
    __slots__ = ()

    @classmethod
    def parse(cls, content_range):
        """
        Parse Content-Range header.
        Format is "bytes=0-524287".
        """
        range_type, range_count = content_range.split('=', 1)
        # There are no other types then "bytes"
        if range_type != 'bytes':
            raise BadRequest(description='Range Header is incorrect')


        range_begin, range_end = range_count.split('-', 1)

        try:
            range_begin = int(range_begin)
        except ValueError as e:
            raise BadRequest(description='Range Header has no start')

        if range_end:
            range_end = int(range_end)
        else:
            range_end = -1

        if range_begin <= range_end or range_end == -1:
            return DownloadRange(range_begin, range_end)

        raise BadRequest(description='Range Header is incorrect')

    @classmethod
    def from_request(cls):
        """
        Read Content-Range from request and parse it
        """
        download_range = request.headers.get('Range')
        if download_range is not None:
            return cls.parse(download_range)

    @property
    def size(self):
        return self.end - self.begin + 1
