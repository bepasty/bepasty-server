import collections
from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for
from werkzeug.exceptions import BadRequest


# safely and comfortably redirect
# some stuff taken from / inspired by http://flask.pocoo.org/snippets/62/

def is_safe_url(target):
    """
    check if target will lead to the same server
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def _redirect_target_url(d, use_referrer, endpoint, **values):
    """
    return redirect url to (in that order):

    - <next> from d
    - referrer (if use_referrer is True)
    - the url for endpoint/values
    """
    targets = [d.get('next'), request.referrer, url_for(endpoint, **values)]
    if not use_referrer:
        del targets[1]
    for target in targets:
        if target and is_safe_url(target):
            return target


# GET - for next 2, you may want to create urls with:
# url_for(endpoint, ..., next=something)

def get_redirect_target(endpoint, **values):
    return _redirect_target_url(request.values, False, endpoint, **values)


def get_redirect_target_referrer(endpoint, **values):
    return _redirect_target_url(request.values, True, endpoint, **values)


# POST - for next 2, you may want this in the form:
# <input type=hidden name="next" value="{{ next or '' }}">

def redirect_next(endpoint, **values):
    return redirect(_redirect_target_url(request.form, False, endpoint, **values))


def redirect_next_referrer(endpoint, **values):
    return redirect(_redirect_target_url(request.form, True, endpoint, **values))


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
        try:
            range_type, range_count = content_range.split(' ', 1)
        except ValueError:
            raise BadRequest(description='Content-Range Header is incorrect')
        # There are no other types then "bytes"
        if range_type != 'bytes':
            raise BadRequest

        try:
            range_count, range_complete = range_count.split('/', 1)
        except ValueError:
            raise BadRequest(description='Content-Range Header is incorrect')

        try:
            # For now, */2000000 format is not supported
            range_begin, range_end = range_count.split('-', 1)

            range_begin = int(range_begin)
            range_end = int(range_end)
        except ValueError:
            raise BadRequest(description='Content-Range Header has invalid range')

        # For now, 0-10/* format is not supported
        try:
            range_complete = int(range_complete)
        except ValueError:
            raise BadRequest(description='Content-Range Header has invalid length')

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
    Work with Range headers.
    """
    __slots__ = ()

    @classmethod
    def parse(cls, content_range):
        """
        Parse Range header.
        Format is "bytes=0-524287".
        """
        try:
            range_type, range_count = content_range.split('=', 1)
        except ValueError:
            raise BadRequest(description='Range Header is incorrect')
        # There are no other types than "bytes"
        if range_type != 'bytes':
            raise BadRequest(description='Range Header is incorrect')

        try:
            range_begin, range_end = range_count.split('-', 1)
        except ValueError:
            raise BadRequest(description='Range Header is incorrect')

        try:
            range_begin = int(range_begin)
        except ValueError:
            raise BadRequest(description='Range Header has invalid first')

        if range_end:
            # For now, set of ranges (e.g. 0-1,2-10) is not supported
            try:
                range_end = int(range_end)
            except ValueError:
                raise BadRequest(description='Range Header has invalid last')
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
