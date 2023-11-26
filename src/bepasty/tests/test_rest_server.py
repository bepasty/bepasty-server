#
# REST api tests
#

import os
import base64
import threading
import time
import copy
import hashlib
import re
from requests.auth import _basic_auth_str
from flask import current_app, url_for, json

import pytest

from ..app import create_app
from .. import config
from ..constants import FILENAME, TYPE, LOCKED, SIZE, COMPLETE, HASH, \
    TIMESTAMP_DOWNLOAD, TIMESTAMP_UPLOAD, TIMESTAMP_MAX_LIFE, TRANSACTION_ID
from ..utils.date_funcs import get_maxlife

UPLOAD_DATA = b"""\
#!/usr/bin/python3

print('hello, world')
"""


class FakeTime:
    """Overwrite time.time to control the timestamp that is used in server"""

    def __init__(self, now=None):
        self.orig = time.time
        self.now = now

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
    """Wait until background threads terminate."""

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()


@pytest.fixture
def client_fixture(tmp_path):
    with FakeTime() as faketime:
        config.PERMISSIONS = {
            'admin': 'admin,list,create,modify,read,delete',
            'full': 'list,create,modify,read,delete',
            'none': '',
        }
        config.STORAGE_FILESYSTEM_DIRECTORY = str(tmp_path)

        app = create_app()
        app.config['TESTING'] = True

        with app.test_client() as client:
            with app.app_context():
                yield app, client, faketime

        wait_background()


class TmpConfig:
    def __init__(self, app, tmp_config=None):
        self.config = app.config
        self.orig_config = copy.deepcopy(app.config)
        self.tmp_config = {} if tmp_config is None else tmp_config

    def __enter__(self):
        self.config.update(self.tmp_config)

    def __exit__(self, exc_type, exc_value, traceback):
        self.config.update(self.orig_config)


class RestUrl:
    def __init__(self, item_id=None):
        self.item_id = item_id

    @property
    def config(self):
        with current_app.test_request_context():
            return url_for('bepasty_apis.api_info')

    @property
    def upload(self):
        with current_app.test_request_context():
            return url_for('bepasty_apis.items')

    @property
    def list(self):
        return self.upload

    @property
    def detail(self):
        with current_app.test_request_context():
            return url_for('bepasty_apis.items_detail', name=self.item_id)

    @property
    def download(self):
        with current_app.test_request_context():
            return url_for('bepasty_apis.items_download', name=self.item_id)

    @property
    def delete(self):
        with current_app.test_request_context():
            return url_for('bepasty_apis.items_delete', name=self.item_id)

    @property
    def modify(self):
        with current_app.test_request_context():
            return url_for('bepasty_apis.items_modify', name=self.item_id)

    @property
    def lock(self):
        with current_app.test_request_context():
            return url_for('bepasty_apis.items_lock', name=self.item_id)

    @property
    def unlock(self):
        with current_app.test_request_context():
            return url_for('bepasty_apis.items_unlock', name=self.item_id)


def add_auth(user, password, headers=None):
    headers = headers if headers is not None else {}
    headers['Authorization'] = _basic_auth_str(user, password)
    return headers


def test_invalid_url(client_fixture):
    _, client, _ = client_fixture

    with client.get('/apis/rest/invalid') as response:
        assert response.status_code == 404


def check_response(response, code, ftype='application/json', check_data=True):
    assert response.status_code == code
    assert response.headers['Content-Type'] == ftype
    if check_data:
        assert int(response.headers['Content-Length']) == len(response.data)


def check_err_response(response, code, check_data=True):
    check_response(response, code, check_data=check_data)
    if check_data:
        assert code == response.json['error']['code']
    # check if doesn't have html tag
    assert not re.match(r'<.+>', response.data.decode())


def check_data_response(response, meta, data, offset=0, total_size=None,
                        check_data=True):
    ftype = meta['file-meta'][TYPE]
    filename = meta['file-meta'][FILENAME]
    if total_size is None:
        total_size = len(data)

    disposition = f'attachment; filename="{filename}"'
    range_str = 'bytes {}-{}/{}'.format(offset, offset + len(data) - 1,
                                        total_size)

    check_response(response, 200, ftype, check_data)
    assert response.headers['Content-Disposition'] == disposition
    assert response.headers['Content-Range'] == range_str
    if check_data:
        assert data == response.data


def check_json_response(response, metas, code=200, check_data=True):
    check_response(response, code, check_data=check_data)
    if check_data:
        assert metas == response.json


def check_upload_response(response, code=201, check_data=True):
    check_json_response(response, {}, code=code, check_data=check_data)

    if code == 200:
        assert len(response.headers[TRANSACTION_ID]) > 0
        return None

    url_prefix = RestUrl().upload + '/'
    assert response.headers['Content-Location'].startswith(url_prefix)
    return response.headers['Content-Location']


def test_auth(client_fixture):
    _, client, _ = client_fixture
    url = RestUrl()

    # basic auth (unknown user)
    with client.get(url.list, headers=add_auth('user', 'invalid')) as response:
        check_err_response(response, 403)
    # basic auth (valid user)
    with client.get(url.list, headers=add_auth('user', 'full')) as response:
        check_response(response, 200)

    # token auth (unknown user)
    with client.get(url.list + '?token=invalid') as response:
        check_err_response(response, 403)
    # token auth (valid user)
    with client.get(url.list + '?token=full') as response:
        check_response(response, 200)


def test_config(client_fixture):
    app, client, _ = client_fixture

    url = RestUrl()

    # get server config (post should fail)
    with client.post(url.config) as response:
        check_err_response(response, 405)

    # get server config
    with client.get(url.config) as response:
        check_response(response, 200)
        assert len(response.json) == 2
        assert response.json['MAX_ALLOWED_FILE_SIZE'] == app.config['MAX_ALLOWED_FILE_SIZE']
        assert response.json['MAX_BODY_SIZE'] == app.config['MAX_BODY_SIZE']

    # get server config (head)
    with client.head(url.config) as response:
        check_response(response, 200, check_data=False)


def _upload(client, data, token=None, filename=None, ftype=None, lifetime=None,
            range_str=None, trans_id=None, encode=True, set_range=True):
    if data:
        payload = base64.b64encode(data) if encode else data
        payload_len = len(payload)
    else:
        payload = None
        payload_len = 0

    headers = {
        'Content-Length': str(payload_len),
    }
    if set_range:
        if range_str is None:
            range_str = f'bytes 0-{payload_len - 1}/{payload_len}'
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

    maxtime = get_maxlife({
        'maxlife_value': lifetime[0],
        'maxlife_unit': lifetime[1]
    }, True)
    maxlife = int(time.time()) + maxtime if maxtime > 0 else maxtime

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
    with _upload(client, data, token, filename, ftype, lifetime) as response:
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

        filename = f'{i}-test.py'
        lifetime = [1, 'YEARS']
        ftype = 'text/x-python'

        with FakeTime(int(time.time()) + i):
            meta = upload(client, data, token='full', filename=filename,
                          ftype=ftype, lifetime=lifetime)

        item_id = os.path.basename(meta['uri'])
        datas[item_id] = data
        metas[item_id] = meta

    assert len(datas) == 2
    assert len(metas) == 2

    return datas, metas


def check_detail_or_download(app, client, item_id, meta, data, download=False):
    url = RestUrl(item_id=item_id)

    url = url.download if download else url.detail

    # post should fail
    with client.post(url) as response:
        check_err_response(response, 405)

    # get with default (no permission)
    with client.get(url) as response:
        check_err_response(response, 403)
    # head with default (no permission)
    with client.head(url) as response:
        check_err_response(response, 403, check_data=False)

    with TmpConfig(app, {'DEFAULT_PERMISSIONS': 'read'}):
        # head with default (has permission)
        with client.head(url) as response:
            if download:
                check_data_response(response, meta, data, check_data=False)
            else:
                check_json_response(response, meta, check_data=False)

        # get with default (has permission)
        with client.get(url) as response:
            if download:
                check_data_response(response, meta, data)
            else:
                check_json_response(response, meta)

    # get with no permission
    with client.get(url, headers=add_auth('user', 'none')) as response:
        check_err_response(response, 403)
    # head with no permission
    with client.head(url, headers=add_auth('user', 'none')) as response:
        check_err_response(response, 403, check_data=False)

    # head with permission
    with client.head(url, headers=add_auth('user', 'full')) as response:
        if download:
            check_data_response(response, meta, data, check_data=False)
        else:
            check_json_response(response, meta, check_data=False)

    # get with permission
    with client.get(url, headers=add_auth('user', 'full')) as response:
        if download:
            check_data_response(response, meta, data)
        else:
            check_json_response(response, meta)


def check_expired(client, item_id, download=False):
    url = RestUrl(item_id=item_id)
    url = url.download if download else url.detail

    # expired items
    with client.get(url, headers=add_auth('user', 'full')) as response:
        check_err_response(response, 404)


def test_upload_basic(client_fixture):
    _, client, _ = client_fixture

    # simple upload without permission
    with _upload(client, UPLOAD_DATA, token='none', filename='test.py',
                 ftype='text/x-python', lifetime=[1, 'FOREVER']) as response:
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
        item_id = os.path.basename(meta['uri'])

        url = RestUrl(item_id)
        # get meta for uploaded item
        with client.get(url.detail, headers=add_auth('user', 'full')) as response:
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

        check_detail_or_download(app, client, item_id, meta, UPLOAD_DATA)
        check_detail_or_download(app, client, item_id, meta, UPLOAD_DATA,
                                 download=True)


def test_upload_range(client_fixture):
    app, client, faketime = client_fixture

    faketime.set_time(100)

    filename = 'test.py'
    ftype = 'text/x-python'

    sep = 10
    data = UPLOAD_DATA[:sep]

    # (invalid no Content-Range:)
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, set_range=False) as response:
        check_err_response(response, 400)

    # Content-Range: invalid (invalid format)
    range_str = 'invalid'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_err_response(response, 400)

    # Content-Range: bytes invalid (invalid format)
    range_str = 'bytes invalid'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_err_response(response, 400)

    # Content-Range: other 0-<sep - 1>/<len(data)> (invalid unit)
    range_str = f'other {0}-{sep - 1}/{len(UPLOAD_DATA)}'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_err_response(response, 400)

    # Content-Range: bytes invalid-<sep - 1>/<len(data)> (invalid first)
    range_str = f'bytes invalid-{sep - 1}/{len(UPLOAD_DATA)}'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_err_response(response, 400)

    # Content-Range: bytes 0-invalid/<len(data)> (invalid last)
    range_str = f'bytes {0}-invalid/{len(UPLOAD_DATA)}'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_err_response(response, 400)

    # Content-Range: bytes <sep - 1>-0/<len(data)> (invalid first > last)
    range_str = f'bytes {sep - 1}-{0}/{len(UPLOAD_DATA)}'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_err_response(response, 400)

    # Content-Range: bytes 0-<sep - 1>/* (not supported)
    range_str = f'bytes {0}-{sep - 1}/*'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_err_response(response, 400)

    # Content-Range: bytes */<len(data)> (not supported)
    range_str = f'bytes */{len(UPLOAD_DATA)}'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_err_response(response, 400)

    # Content-Range: bytes */* (not supported)
    range_str = 'bytes */*'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_err_response(response, 400)

    # upload first part of data
    range_str = f'bytes {0}-{sep - 1}/{len(UPLOAD_DATA)}'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_upload_response(response, 200)

    # upload remainder of data
    data = UPLOAD_DATA[sep:]
    range_str = 'bytes {}-{}/{}'.format(sep, len(UPLOAD_DATA) - 1,
                                        len(UPLOAD_DATA))
    with _upload(client, data, token='full', range_str=range_str,
                 trans_id=response.headers[TRANSACTION_ID]) as response:
        uri = check_upload_response(response)
    item_id = os.path.basename(uri)

    # check a uploaded item
    meta = make_meta(UPLOAD_DATA, filename=filename, ftype=ftype, uri=uri)
    check_detail_or_download(app, client, item_id, meta, UPLOAD_DATA)
    check_detail_or_download(app, client, item_id, meta, UPLOAD_DATA,
                             download=True)

    # upload again with item.data.size != start position (invalid position)
    data = UPLOAD_DATA[sep + 1:]
    range_str = 'bytes {}-{}/{}'.format(sep + 1, len(UPLOAD_DATA) - 1,
                                        len(UPLOAD_DATA))
    with _upload(client, data, token='full', range_str=range_str,
                 trans_id=response.headers[TRANSACTION_ID]) as response:
        check_err_response(response, 409)


def test_bad_data(client_fixture):
    app, client, _ = client_fixture

    filename = 'test.py'
    ftype = 'text/x-python'

    # upload without Content-Length
    range_str = f'bytes 0-{len(UPLOAD_DATA) - 1}/{len(UPLOAD_DATA)}'
    with _upload(client, None, token='full', filename=filename,
                 ftype=ftype, range_str=range_str, encode=False) as response:
        check_err_response(response, 400)

    # upload invalid base64 encode
    range_str = f'bytes 0-{len(UPLOAD_DATA) - 1}/{len(UPLOAD_DATA)}'
    with _upload(client, UPLOAD_DATA, token='full', filename=filename,
                 ftype=ftype, range_str=range_str, encode=False) as response:
        check_err_response(response, 400)

    # server must not have left garbage files
    assert len(os.listdir(app.config['STORAGE_FILESYSTEM_DIRECTORY'])) == 0


def test_upload_maxlife(client_fixture):
    """upload maxlife"""

    _, client, _ = client_fixture

    lifetime = ['foo', 'MINUTES']
    with _upload(client, UPLOAD_DATA, token='full', lifetime=lifetime) as response:
        assert response.status_code == 400

    lifetime = ['1', 'foo']
    with _upload(client, UPLOAD_DATA, token='full', lifetime=lifetime) as response:
        assert response.status_code == 400


def test_upload_transaction_id(client_fixture):
    app, client, faketime = client_fixture

    faketime.set_time(100)

    sep = 10
    data = UPLOAD_DATA[sep:]
    range_str = 'bytes {}-{}/{}'.format(sep, len(UPLOAD_DATA) - 1,
                                        len(UPLOAD_DATA))

    # upload with invalid Transaction-ID
    trans_id = 'invalid'
    with _upload(client, data, token='full', range_str=range_str,
                 trans_id=trans_id) as response:
        check_err_response(response, 400)

    # upload with Transaction-ID for invalid filename
    trans_id = base64.b64encode(b'invalid').decode()
    with _upload(client, data, token='full', range_str=range_str,
                 trans_id=trans_id) as response:
        check_err_response(response, 400)


def test_upload_too_big(client_fixture):
    app, client, _ = client_fixture

    # upload too big size
    size = 10000
    with TmpConfig(app, {'MAX_ALLOWED_FILE_SIZE': size}):
        ftype = 'text/x-bepasty-list'
        data = bytes(b'a' * (size + 10))
        with _upload(client, data, token='full', ftype=ftype) as response:
            check_err_response(response, 413)


def test_list_basic(client_fixture):
    app, client, faketime = client_fixture

    url = RestUrl()
    faketime.set_time(100)

    datas, metas = upload_files(client)

    # list with default (no permission)
    with client.get(url.list) as response:
        check_err_response(response, 403)
    with client.head(url.list) as response:
        check_err_response(response, 403, check_data=False)

    # list with default (has permission)
    with TmpConfig(app, {'DEFAULT_PERMISSIONS': 'list'}):
        with client.get(url.list) as response:
            check_json_response(response, metas)
        with client.head(url.list) as response:
            check_json_response(response, metas, check_data=False)

    # list with no permission
    with client.get(url.list, headers=add_auth('user', 'none')) as response:
        check_err_response(response, 403)
    with client.head(url.list, headers=add_auth('user', 'none')) as response:
        check_err_response(response, 403, check_data=False)

    # list with permission
    with client.get(url.list, headers=add_auth('user', 'full')) as response:
        check_json_response(response, metas)
    with client.head(url.list, headers=add_auth('user', 'full')) as response:
        check_json_response(response, metas, check_data=False)

    # adjust time to exceed lifetime
    faketime.set_time(3600 * 24 * 365 * 2)
    # list for expired items
    with client.get(url.list, headers=add_auth('user', 'full')) as response:
        check_json_response(response, {})


def test_detail_basic(client_fixture):
    app, client, faketime = client_fixture

    faketime.set_time(100)

    datas, metas = upload_files(client)

    for item_id in metas.keys():
        data = datas[item_id]
        meta = metas[item_id]

        check_detail_or_download(app, client, item_id, meta, data)

        # detail of expired item
        faketime.set_time(3600 * 24 * 365 * 2)
        check_expired(client, item_id)
        # check again (should be deleted already)
        faketime.set_time(100)
        check_expired(client, item_id)


def test_download_basic(client_fixture):
    app, client, faketime = client_fixture

    faketime.set_time(100)

    datas, metas = upload_files(client)

    for item_id in metas.keys():
        data = datas[item_id]
        meta = metas[item_id]

        check_detail_or_download(app, client, item_id, meta, data,
                                 download=True)

        # download of expired item
        faketime.set_time(3600 * 24 * 365 * 2)
        check_expired(client, item_id, download=True)
        # check again (should be deleted already)
        faketime.set_time(100)
        check_expired(client, item_id)


def test_download_range(client_fixture):
    _, client, faketime = client_fixture

    faketime.set_time(100)

    datas, metas = upload_files(client)

    for item_id in metas.keys():
        data = datas[item_id]
        meta = metas[item_id]

        url = RestUrl(item_id=item_id)
        headers = add_auth('user', 'full')

        # Range: other (invalid format)
        offset = 0
        limit = 10
        headers['Range'] = 'other'
        with client.get(url.download, headers=headers) as response:
            check_err_response(response, 400)

        # Range: bytes=invalid (invalid format)
        offset = 0
        limit = 10
        headers['Range'] = 'bytes=invalid'
        with client.get(url.download, headers=headers) as response:
            check_err_response(response, 400)

        # Range: other=0-10 (invalid unit)
        offset = 0
        limit = 10
        headers['Range'] = f'other={offset}-{limit - 1}'
        with client.get(url.download, headers=headers) as response:
            check_err_response(response, 400)

        # Range: bytes=invalid-10 (invalid first)
        offset = 0
        limit = 10
        headers['Range'] = f'bytes=invalid-{limit - 1}'
        with client.get(url.download, headers=headers) as response:
            check_err_response(response, 400)

        # Range: bytes=0-invalid (invalid last)
        offset = 0
        limit = 10
        headers['Range'] = f'other={offset}-invalid'
        with client.get(url.download, headers=headers) as response:
            check_err_response(response, 400)

        # Range: bytes=10-0 (invalid first > last)
        offset = 0
        limit = 10
        headers['Range'] = f'bytes={limit - 1}-{offset}'
        with client.get(url.download, headers=headers) as response:
            check_err_response(response, 400)

        # Range: bytes=0-9,10-<limit - 1> (not supported for now)
        offset = 0
        limit = len(data)
        headers['Range'] = f'bytes={offset}-9,10-{limit - 1}'
        with client.get(url.download, headers=headers) as response:
            check_err_response(response, 400)

        # Range: bytes=0-10
        offset = 0
        limit = 10
        headers['Range'] = f'bytes={offset}-{limit - 1}'
        with client.get(url.download, headers=headers) as response:
            check_data_response(response, meta, data[offset:limit],
                                offset=offset, total_size=len(data))

        # Range: bytes=-9
        # FIXME: suffix-byte-range-spec is not supported for now
        offset = 0
        limit = 10
        headers['Range'] = f'bytes=-{limit - 1}'
        with client.get(url.download, headers=headers) as response:
            check_err_response(response, 400)

        # Range: bytes=10-<limit - 1>
        offset = 10
        limit = len(data)
        headers['Range'] = f'bytes={offset}-{limit - 1}'
        with client.get(url.download, headers=headers) as response:
            check_data_response(response, meta, data[offset:limit],
                                offset=offset, total_size=len(data))

        # Range: bytes=10-
        offset = 10
        limit = len(data)
        headers['Range'] = f'bytes={offset}-'
        with client.get(url.download, headers=headers) as response:
            check_data_response(response, meta, data[offset:limit],
                                offset=offset, total_size=len(data))


def test_modify(client_fixture):
    app, client, _ = client_fixture

    meta = upload(client, UPLOAD_DATA, token='full', filename='test.py',
                  ftype='text/x-python', lifetime=[1, 'FOREVER'])

    item_id = os.path.basename(meta['uri'])
    url = RestUrl(item_id)

    check_detail_or_download(app, client, item_id, meta, None)

    headers = {'Content-Type': 'application/json'}

    # no permission
    with client.post(url.modify, headers=headers, data='{}') as response:
        check_err_response(response, 403)

    headers = add_auth('user', 'full', headers)

    # invalid name
    with client.post(RestUrl('abcdefgh').modify, headers=headers, data='{}') as response:
        check_err_response(response, 404)

    # invalid Content-Type
    with client.post(url.modify, headers=add_auth('user', 'full'), data='{}') as response:
        check_err_response(response, 415)

    # invalid json
    with client.post(url.modify, headers=headers, data='') as response:
        check_err_response(response, 400)

    # change filename
    filename = 'test2.py'
    meta['file-meta'][FILENAME] = filename
    data = json.dumps({FILENAME: filename})
    with client.post(url.modify, headers=headers, data=data) as response:
        check_json_response(response, {})

    check_detail_or_download(app, client, item_id, meta, None)

    # change type
    content_type = 'text/plain'
    meta['file-meta'][TYPE] = content_type
    data = json.dumps({TYPE: content_type})
    with client.post(url.modify, headers=headers, data=data) as response:
        check_json_response(response, {})

    check_detail_or_download(app, client, item_id, meta, None)


def test_delete_basic(client_fixture):
    app, client, faketime = client_fixture

    faketime.set_time(100)

    datas, metas = upload_files(client)

    url = RestUrl('abcdefgh')

    # delete ENOENT item
    with client.post(url.delete, headers=add_auth('user', 'admin')) as response:
        check_err_response(response, 404)

    for item_id in metas.keys():
        url = RestUrl(item_id)

        # no permission
        with client.post(url.delete, headers=add_auth('user', 'invalid')) as response:
            check_err_response(response, 403)

        # has permission
        with client.post(url.delete, headers=add_auth('user', 'full')) as response:
            check_json_response(response, {})

        # should already be deleted
        with client.post(url.delete, headers=add_auth('user', 'full')) as response:
            check_err_response(response, 404)


def test_lock_basic(client_fixture):
    app, client, faketime = client_fixture

    faketime.set_time(100)

    datas, metas = upload_files(client)

    url = RestUrl('abcdefgh')

    for u in (url.lock, url.unlock):
        # lock/unlock ENOENT item
        with client.post(u, headers=add_auth('user', 'admin')) as response:
            check_err_response(response, 404)

    for item_id in metas.keys():
        url = RestUrl(item_id)

        for u in (url.lock, url.unlock):
            # lock/unlock, no permission (invalid user)
            with client.post(u, headers=add_auth('user', 'invalid')) as response:
                check_err_response(response, 403)

            # lock/unlock, no permission (not admin)
            with client.post(u, headers=add_auth('user', 'full')) as response:
                check_err_response(response, 403)

            # lock/unlock, has permission
            with client.post(u, headers=add_auth('user', 'admin')) as response:
                check_json_response(response, {})

        # lock item
        with client.post(url.lock, headers=add_auth('user', 'admin')) as response:
            check_json_response(response, {})

        # download locked item (should fail)
        with client.get(url.download, headers=add_auth('user', 'full')) as response:
            check_err_response(response, 403)

        # download locked item with admin (should succeed)
        with client.get(url.download, headers=add_auth('user', 'admin')) as response:
            check_data_response(response, metas[item_id], datas[item_id])

        # modify locked item (should fail)
        headers = add_auth('user', 'full', {'Content-Type': 'application/json'})
        with client.post(url.modify, headers=headers, data='{}') as response:
            check_err_response(response, 403)

        # modify locked item with admin (should succeed)
        headers = add_auth('user', 'admin', {'Content-Type': 'application/json'})
        with client.post(url.modify, headers=headers, data='{}') as response:
            check_json_response(response, {})

        # delete locked item (should fail)
        with client.post(url.delete, headers=add_auth('user', 'full')) as response:
            check_err_response(response, 403)

        # delete locked item with admin (should succeed)
        with client.post(url.delete, headers=add_auth('user', 'admin')) as response:
            check_json_response(response, {})

        # deleted item
        with client.post(url.delete, headers=add_auth('user', 'admin')) as response:
            check_err_response(response, 404)


def test_incomplete(client_fixture):
    _, client, _ = client_fixture

    filename = 'test.py'
    ftype = 'text/x-python'

    # upload a half of data to make incomplete
    sep = 10
    data = UPLOAD_DATA[:sep]
    range_str = f'bytes {0}-{sep - 1}/{len(UPLOAD_DATA)}'
    with _upload(client, data, token='full', filename=filename,
                 ftype=ftype, range_str=range_str) as response:
        check_upload_response(response, 200)
        assert len(response.headers[TRANSACTION_ID]) > 0

    # get incomplete item from list
    url = RestUrl()
    headers = add_auth('user', 'full')
    with client.get(url.list, headers=headers) as response:
        print(f'{response}')
        check_response(response, 200)
        assert len(response.json) == 1

        item_id = list(response.json.keys())[0]

    url = RestUrl(item_id)

    # detail should error with incomplete
    with client.get(url.detail, headers=add_auth('user', 'full')) as response:
        check_err_response(response, 409)

    # download should error with incomplete
    with client.get(url.download, headers=add_auth('user', 'full')) as response:
        check_err_response(response, 409)

    # modify should error with incomplete
    headers = add_auth('user', 'full', {'Content-Type': 'application/json'})
    with client.post(url.modify, headers=headers, data='{}') as response:
        check_err_response(response, 409)

    # lock should error with incomplete
    with client.post(url.lock, headers=add_auth('user', 'admin')) as response:
        check_err_response(response, 409)

    # unlock should error with incomplete
    with client.post(url.unlock, headers=add_auth('user', 'admin')) as response:
        check_err_response(response, 409)

    # delete should error with incomplete
    with client.post(url.delete, headers=add_auth('user', 'full')) as response:
        check_err_response(response, 409)

    # delete by admin with incomplete should succeed
    with client.post(url.delete, headers=add_auth('user', 'admin')) as response:
        check_json_response(response, {})


def test_magic(client_fixture):
    app, client, _ = client_fixture

    try:
        import magic
        assert magic is not None  # suppress flake8 warning
    except ImportError:
        pytest.skip("skipping test, no python-magic installed")
    else:
        with TmpConfig(app, {'USE_PYTHON_MAGIC': True}):
            filename = None
            ftype = None

            # upload a half of data to make incomplete with auto mime
            # detection (meta has 'type-hint' internally)
            sep = 10
            data = UPLOAD_DATA[:sep]
            range_str = f'bytes {0}-{sep - 1}/{len(UPLOAD_DATA)}'
            with _upload(client, data, token='full', filename=filename,
                         ftype=ftype, range_str=range_str) as response:
                check_upload_response(response, 200)
                assert len(response.headers[TRANSACTION_ID]) > 0
                trans_id = response.headers[TRANSACTION_ID]

            # get incomplete item from list
            url = RestUrl()
            headers = add_auth('user', 'full')
            with client.get(url.list, headers=headers) as response:
                check_response(response, 200)
                assert len(response.json) == 1

                fid = list(response.json.keys())[0]
                meta = list(response.json.values())[0]

            # 'type-hint' should be invisible
            assert meta['file-meta'] is not None
            assert meta['file-meta'].get('type-hint') is None

            # 'type' is 'application/octet-stream' for now
            assert meta['file-meta'][TYPE] == 'application/octet-stream'

            # complete upload
            data = UPLOAD_DATA[sep:]
            range_str = 'bytes {}-{}/{}'.format(sep, len(UPLOAD_DATA) - 1,
                                                len(UPLOAD_DATA))
            with _upload(client, data, token='full', range_str=range_str,
                         trans_id=trans_id) as response:
                check_upload_response(response)

            # get detail to check python-magic auto detection
            url = RestUrl(fid)
            with client.get(url.detail, headers=add_auth('user', 'full')) as response:
                check_json_response(response, None, check_data=False)

                assert response.json['file-meta'] is not None
                assert response.json['file-meta'][TYPE] in ('text/x-python', 'text/x-script.python')
