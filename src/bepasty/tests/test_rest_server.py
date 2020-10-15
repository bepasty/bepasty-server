#
# REST api tests
#

import os
import base64
import threading
import time
import hashlib
from requests.auth import _basic_auth_str

import pytest

from ..app import create_app
from ..config import Config
from ..constants import FILENAME, TYPE, LOCKED, SIZE, COMPLETE, HASH, \
    TIMESTAMP_DOWNLOAD, TIMESTAMP_UPLOAD, TIMESTAMP_MAX_LIFE, TRANSACTION_ID
from ..utils.date_funcs import time_unit_to_sec

UPLOAD_DATA = b"""\
#!/usr/bin/python3

print('hello, world')
"""


class FakeTime:
    """Overwrite time.time to control the timestamp that is used in server"""

    def __init__(self, now=None):
        self.orig = time.time
        self.now = now
        self.set_time(self.now)

    def set_time(self, now=None):
        self.now = now
        if now and time.time != self.get_time:
            time.time = self.get_time
        elif now is None and time.time == self.get_time:
            time.time = self.orig

    def get_time(self):
        return self.now

    def __enter__(self):
        self.set_time(self.now)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.set_time(None)


def wait_background():
    """Wait background threads"""

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()


@pytest.fixture
def client_fixture(tmp_path):
    with FakeTime() as faketime:
        Config.PERMISSIONS = {
            'admin': 'admin,list,create,read,delete',
            'full': 'list,create,read,delete',
            'none': '',
        }
        Config.STORAGE_FILESYSTEM_DIRECTORY = str(tmp_path)

        app = create_app()
        app.config['TESTING'] = True

        with app.test_client() as client:
            yield app, client, faketime

        wait_background()


class TmpConfig:
    def __init__(self, app, tmp_config={}):
        self.config = app.config
        self.orig_config = {}
        self.tmp_config = tmp_config
        for k, v in tmp_config.items():
            self.orig_config[k] = self.config[k]

    def __enter__(self):
        for k, v in self.tmp_config.items():
            self.config[k] = v

    def __exit__(self, exc_type, exc_value, traceback):
        for k, v in self.orig_config.items():
            self.config[k] = self.orig_config[k]


class RestUrl:
    def __init__(self, fid=None):
        self.fid = fid

    @property
    def config(self):
        return '/apis/rest'

    @property
    def upload(self):
        return '/apis/rest/items'

    @property
    def list(self):
        return self.upload

    @property
    def detail(self):
        return '/apis/rest/items/{}'.format(self.fid)

    @property
    def download(self):
        return '/apis/rest/items/{}/download'.format(self.fid)


def add_auth(user, password, headers=None):
    if headers is None:
        headers = dict()
    headers.update({'Authorization': _basic_auth_str(user, password)})
    return headers


def test_invalid_url(client_fixture):
    _, client, _ = client_fixture

    # invalid url
    response = client.get('/apis/rest/foo')
    assert response.status_code == 404


def check_response(response, code, ftype='application/json', check_data=True):
    assert response.status_code == code
    assert response.headers['Content-Type'] == ftype
    if check_data:
        assert int(response.headers['Content-Length']) == len(response.data)


def check_err_response(response, code, check_data=True):
    check_response(response, code, 'text/html; charset=utf-8', check_data)


def check_data_response(response, meta, data, offset=None, total_size=None,
                        check_data=True):
    ftype = meta['file-meta'][TYPE]
    filename = meta['file-meta'][FILENAME]
    if offset is None:
        offset = 0
    if total_size is None:
        total_size = len(data)

    dispoition = 'attachment; filename="{}"'.format(filename)
    range_str = 'bytes {}-{}/{}'.format(offset, offset + len(data) - 1,
                                        total_size)

    check_response(response, 200, ftype, check_data)
    assert response.headers['Content-Disposition'] == dispoition
    assert response.headers['Content-Range'] == range_str
    if check_data:
        assert data == response.data


def check_json_response(response, metas, check_data=True):
    check_response(response, 200, check_data=check_data)
    if check_data:
        assert metas == response.json


def check_upload_response(response, code=201, check_data=True):
    check_response(response, code, 'text/html; charset=utf-8', check_data)

    if code == 200:
        assert len(response.headers[TRANSACTION_ID]) > 0
        return None

    assert response.headers['Content-Location'].startswith('/apis/rest/items/')
    return response.headers['Content-Location']


def test_auth(client_fixture):
    _, client, _ = client_fixture
    url = RestUrl()

    # basic auth (unknown user)
    response = client.get(url.list, headers=add_auth('user', 'invalid'))
    check_err_response(response, 403)
    # basic auth (valid user)
    response = client.get(url.list, headers=add_auth('user', 'full'))
    check_response(response, 200)

    # token auth (unknown user)
    response = client.get(url.list + '?token=invalid')
    check_err_response(response, 403)
    # token auth (valid user)
    response = client.get(url.list + '?token=full')
    check_response(response, 200)


def test_config(client_fixture):
    app, client, _ = client_fixture

    url = RestUrl()

    # get server config (post should fail)
    response = client.post(url.config)
    check_err_response(response, 405)

    # get server config
    response = client.get(url.config)
    check_response(response, 200)
    assert len(response.json) == 2
    assert response.json['MAX_ALLOWED_FILE_SIZE'] == app.config['MAX_ALLOWED_FILE_SIZE']
    assert response.json['MAX_BODY_SIZE'] == app.config['MAX_BODY_SIZE']

    # get server config (head)
    response = client.head(url.config)
    check_response(response, 200, check_data=False)


def _upload(client, data, token=None, filename=None, ftype=None, lifetime=None,
            range_str=None, trans_id=None, no_encode=False):
    if data:
        if no_encode:
            payload = data
        else:
            payload = base64.b64encode(data)
        payload_len = len(payload)
    else:
        payload = None
        payload_len = 0

    headers = {
        'Content-Length': str(payload_len),
    }
    if range_str is None:
        range_str = 'bytes 0-{}/{}'.format(payload_len - 1, payload_len)
    headers['Content-Range'] = range_str
    if filename is not None:
        headers['Content-Filename'] = filename
    if ftype is not None:
        headers['Content-Type'] = ftype
    if lifetime:
        headers['Maxlife-Value'] = str(lifetime[0])
        headers['Maxlife-Unit'] = lifetime[1]
    if trans_id is not None:
        headers[TRANSACTION_ID] = trans_id
    if token is not None:
        add_auth('user', token, headers)

    response = client.post(RestUrl().upload, headers=headers, data=payload)
    # FIXME: without waiting for background hash compute, following
    # detail request may not have hash yet
    wait_background()

    return response


def make_meta(data, filename=None, ftype=None, lifetime=None, uri=None):
    h = hashlib.sha256()
    h.update(data)

    if lifetime is None:
        # default maxlife is 1 MONTHS
        lifetime = [1, 'MONTHS']
    maxlife = int(time.time()) + time_unit_to_sec(lifetime[0], lifetime[1])

    meta = {
        'file-meta': {
            COMPLETE: True,
            FILENAME: filename,
            HASH: h.hexdigest(),
            LOCKED: False,
            SIZE: len(data),
            TIMESTAMP_DOWNLOAD: 0,
            TIMESTAMP_MAX_LIFE: maxlife,
            TIMESTAMP_UPLOAD: int(time.time()),
            TYPE: ftype,
        },
        'uri': uri,
    }
    return meta


def upload(client, data, token=None, filename=None, ftype=None, lifetime=None):
    response = _upload(client, data, token, filename, ftype, lifetime)
    uri = check_upload_response(response)

    return make_meta(data, filename, ftype, lifetime, uri)


def upload_files(client):
    datas = {}
    metas = {}

    for i in (1, 2):

        data = """\
#!/usr/bin/python3

print('hello,world {}')
""".format(i).encode()

        filename = '{}-test.py'.format(i)
        lifetime = [1, 'YEARS']
        ftype = 'text/x-python'

        with FakeTime(int(time.time()) + i):
            meta = upload(client, data, token='full', filename=filename,
                          ftype=ftype, lifetime=lifetime)

        fid = os.path.basename(meta['uri'])
        datas[fid] = data
        metas[fid] = meta

    assert len(datas) == 2
    assert len(metas) == 2

    return datas, metas


def check_detail_or_download(app, client, fid, meta, data, download=False):
    url = RestUrl(fid=fid)

    if download:
        url = url.download
    else:
        url = url.detail

    # post should fail
    response = client.post(url)
    check_err_response(response, 405)

    # get with default (no permission)
    response = client.get(url)
    check_err_response(response, 403)
    # head with default (no permission)
    response = client.head(url)
    check_err_response(response, 403, check_data=False)

    with TmpConfig(app, {'DEFAULT_PERMISSIONS': 'read'}):
        # head with default (has permission)
        response = client.head(url)
        if download:
            check_data_response(response, meta, data, check_data=False)
        else:
            check_json_response(response, meta, check_data=False)

        # get with default (has permission)
        response = client.get(url)
        if download:
            check_data_response(response, meta, data)
        else:
            check_json_response(response, meta)

    # get with no permission
    response = client.get(url, headers=add_auth('user', 'none'))
    check_err_response(response, 403)
    # head with no permission
    response = client.head(url, headers=add_auth('user', 'none'))
    check_err_response(response, 403, check_data=False)

    # head with permission
    response = client.head(url, headers=add_auth('user', 'full'))
    if download:
        check_data_response(response, meta, data, check_data=False)
    else:
        check_json_response(response, meta, check_data=False)

    # get with permission
    response = client.get(url, headers=add_auth('user', 'full'))
    if download:
        check_data_response(response, meta, data)
    else:
        check_json_response(response, meta)


def check_expired(client, fid, download=False):
    url = RestUrl(fid=fid)
    if download:
        url = url.download
    else:
        url = url.detail

    # expired items
    response = client.get(url, headers=add_auth('user', 'full'))
    check_err_response(response, 404)


def test_upload_basic(client_fixture):
    _, client, _ = client_fixture

    # simple upload without permission
    response = _upload(client, UPLOAD_DATA, token='none', filename='test.py',
                       ftype='text/x-python', lifetime=[1, 'FOREVER'])
    check_err_response(response, 403)

    # simple upload with permission
    upload(client, UPLOAD_DATA, token='full', filename='test.py',
           ftype='text/x-python', lifetime=[1, 'FOREVER'])


def test_upload_params(client_fixture):
    app, client, faketime = client_fixture

    faketime.set_time(100)

    for filename, ftype in ((None, None), ('test.py', None), (None, 'text/plain')):
        # upload without filename and/or ftype
        meta = upload(client, UPLOAD_DATA, token='full',
                      filename=filename, ftype=ftype)
        fid = os.path.basename(meta['uri'])

        url = RestUrl(fid)
        # get meta for uploaded item
        response = client.get(url.detail, headers=add_auth('user', 'full'))
        check_json_response(response, None, check_data=False)
        assert len(response.json) > 0
        # copy generated meta
        if filename:
            assert response.json['file-meta'][FILENAME] == filename
        else:
            assert len(response.json['file-meta'][FILENAME]) > 0
            meta['file-meta'][FILENAME] = response.json['file-meta'][FILENAME]
        if ftype:
            assert response.json['file-meta'][TYPE] == ftype
        else:
            assert len(response.json['file-meta'][TYPE]) > 0
            meta['file-meta'][TYPE] = response.json['file-meta'][TYPE]

        check_detail_or_download(app, client, fid, meta, UPLOAD_DATA)
        check_detail_or_download(app, client, fid, meta, UPLOAD_DATA,
                                 download=True)


def test_upload_range(client_fixture):
    app, client, faketime = client_fixture

    faketime.set_time(100)

    filename = 'test.py'
    ftype = 'text/x-python'

    # upload a first half of data
    sep = 10
    data = UPLOAD_DATA[:sep]
    range_str = 'bytes {}-{}/{}'.format(0, sep - 1, sep + 1)
    response = _upload(client, data, token='full', filename=filename,
                       ftype=ftype, range_str=range_str)
    check_upload_response(response, 200)

    # upload a rest of data
    data = UPLOAD_DATA[sep:]
    range_str = 'bytes {}-{}/{}'.format(sep, len(UPLOAD_DATA) - 1,
                                        len(UPLOAD_DATA))
    response = _upload(client, data, token='full', range_str=range_str,
                       trans_id=response.headers[TRANSACTION_ID])
    uri = check_upload_response(response)
    fid = os.path.basename(uri)

    # check a uploaded item
    meta = make_meta(UPLOAD_DATA, filename=filename, ftype=ftype, uri=uri)
    check_detail_or_download(app, client, fid, meta, UPLOAD_DATA)
    check_detail_or_download(app, client, fid, meta, UPLOAD_DATA, download=True)

    # upload again with not append position
    data = UPLOAD_DATA[sep + 1:]
    range_str = 'bytes {}-{}/{}'.format(sep + 1, len(UPLOAD_DATA) - 1,
                                        len(UPLOAD_DATA))
    response = _upload(client, data, token='full', range_str=range_str,
                       trans_id=response.headers[TRANSACTION_ID])
    check_err_response(response, 409)


def test_bad_data(client_fixture):
    app, client, _ = client_fixture

    filename = 'test.py'
    ftype = 'text/x-python'

    # upload invalid base64 encode
    range_str = 'bytes 0-{}/{}'.format(len(UPLOAD_DATA) - 1, len(UPLOAD_DATA))
    response = _upload(client, UPLOAD_DATA, token='full', filename=filename,
                       ftype=ftype, range_str=range_str, no_encode=True)
    check_err_response(response, 400)

    # server should not left garbage files
    assert len(os.listdir(app.config['STORAGE_FILESYSTEM_DIRECTORY'])) == 0


def test_upload_too_big(client_fixture):
    app, client, _ = client_fixture

    # upload too big size
    size = 10000
    with TmpConfig(app, {'MAX_ALLOWED_FILE_SIZE': size}):
        ftype = 'text/x-bepasty-list'
        data = bytes(b'a' * (size + 10))
        response = _upload(client, data, token='full', ftype=ftype)
        check_err_response(response, 413)


def test_list_basic(client_fixture):
    app, client, faketime = client_fixture

    url = RestUrl()
    faketime.set_time(100)

    datas, metas = upload_files(client)

    # list with default (no permission)
    response = client.get(url.list)
    check_err_response(response, 403)
    response = client.head(url.list)
    check_err_response(response, 403, check_data=False)

    # list with default (has permission)
    with TmpConfig(app, {'DEFAULT_PERMISSIONS': 'list'}):
        response = client.get(url.list)
        check_json_response(response, metas)
        response = client.head(url.list)
        check_json_response(response, metas, check_data=False)

    # list with no permission
    response = client.get(url.list, headers=add_auth('user', 'none'))
    check_err_response(response, 403)
    response = client.head(url.list, headers=add_auth('user', 'none'))
    check_err_response(response, 403, check_data=False)

    # list with permission
    response = client.get(url.list, headers=add_auth('user', 'full'))
    check_json_response(response, metas)
    response = client.head(url.list, headers=add_auth('user', 'full'))
    check_json_response(response, metas, check_data=False)

    # adjust time to exceed lifetime
    faketime.set_time(3600 * 24 * 365 * 2)
    # list for expired items
    response = client.get(url.list, headers=add_auth('user', 'full'))
    check_json_response(response, {})


def test_detail_basic(client_fixture):
    app, client, faketime = client_fixture

    faketime.set_time(100)

    datas, metas = upload_files(client)

    for fid in metas.keys():
        data = datas[fid]
        meta = metas[fid]

        check_detail_or_download(app, client, fid, meta, data)

        # detail of expired item
        faketime.set_time(3600 * 24 * 365 * 2)
        check_expired(client, fid)
        # check again (should be deleted already)
        faketime.set_time(100)
        check_expired(client, fid)


def test_download_basic(client_fixture):
    app, client, faketime = client_fixture

    faketime.set_time(100)

    datas, metas = upload_files(client)

    for fid in metas.keys():
        data = datas[fid]
        meta = metas[fid]

        check_detail_or_download(app, client, fid, meta, data, download=True)

        # download of expired item
        faketime.set_time(3600 * 24 * 365 * 2)
        check_expired(client, fid, download=True)
        # check again (should be deleted already)
        faketime.set_time(100)
        check_expired(client, fid)


def test_download_range(client_fixture):
    _, client, faketime = client_fixture

    faketime.set_time(100)

    datas, metas = upload_files(client)

    for fid in metas.keys():
        data = datas[fid]
        meta = metas[fid]

        url = RestUrl(fid=fid)
        headers = add_auth('user', 'full')

        # Range: other=0-10 (invalid unit)
        offset = 0
        limit = 10
        headers['Range'] = 'other={}-{}'.format(offset, limit - 1)
        response = client.get(url.download, headers=headers)
        check_err_response(response, 400)

        # Range: bytes=10-0 (invalid range)
        offset = 0
        limit = 10
        headers['Range'] = 'bytes={}-{}'.format(limit - 1, offset)
        response = client.get(url.download, headers=headers)
        check_err_response(response, 400)

        # Range: bytes=0-10
        offset = 0
        limit = 10
        headers['Range'] = 'bytes={}-{}'.format(offset, limit - 1)
        response = client.get(url.download, headers=headers)
        check_data_response(response, meta, data[offset:limit], offset=offset,
                            total_size=len(data))

        # Range: bytes=-9
        # FIXME: suffix-byte-range-spec is not supported for now
        offset = 0
        limit = 10
        headers['Range'] = 'bytes=-{}'.format(limit - 1)
        response = client.get(url.download, headers=headers)
        check_err_response(response, 400)

        # Range: bytes=10-<limit - 1>
        offset = 10
        limit = len(data)
        headers['Range'] = 'bytes={}-{}'.format(offset, limit - 1)
        response = client.get(url.download, headers=headers)
        check_data_response(response, meta, data[offset:limit], offset=offset,
                            total_size=len(data))

        # Range: bytes=10-
        offset = 10
        limit = len(data)
        headers['Range'] = 'bytes={}-'.format(offset)
        response = client.get(url.download, headers=headers)
        check_data_response(response, meta, data[offset:limit], offset=offset,
                            total_size=len(data))


def test_incomplete(client_fixture):
    _, client, _ = client_fixture

    filename = 'test.py'
    ftype = 'text/x-python'

    # upload a half of data to make incomplete
    sep = 10
    data = UPLOAD_DATA[:sep]
    range_str = 'bytes {}-{}/{}'.format(0, sep - 1, len(UPLOAD_DATA))
    response = _upload(client, data, token='full', filename=filename,
                       ftype=ftype, range_str=range_str)
    check_upload_response(response, 200)

    # get incomplete item from list
    url = RestUrl()
    headers = add_auth('user', 'full')
    response = client.get(url.list, headers=headers)
    check_response(response, 200)
    assert len(response.json) == 1

    fid = list(response.json.keys())[0]
    # meta = list(response.json.values())[0]

    # detail should error with incomplete
    url = RestUrl(fid)
    response = client.get(url.detail, headers=add_auth('user', 'full'))
    check_err_response(response, 409)

    # download should error with incomplete
    response = client.get(url.download, headers=add_auth('user', 'full'))
    check_err_response(response, 409)
