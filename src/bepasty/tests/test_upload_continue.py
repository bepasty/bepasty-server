#
# Continued (chunked) uploads must only write into uploads in progress
#

import base64
import io

import pytest

from ..app import create_app
from ..config import Config
from ..constants import COMPLETE, LOCKED, SIZE


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, 'STORAGE_FILESYSTEM_DIRECTORY', str(tmp_path))
    monkeypatch.setattr(Config, 'SECRET_KEY', 'secret')
    monkeypatch.setattr(Config, 'DEFAULT_PERMISSIONS', '')
    monkeypatch.setattr(Config, 'PERMISSIONS', {
        'admin': 'admin,list,create,modify,read,delete',
        'creator': 'create,read',
    })
    monkeypatch.delenv('BEPASTY_CONFIG', raising=False)
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def upload_complete(client, text=b'original content'):
    rv = client.post('/+upload?token=admin', data={'file': (io.BytesIO(text), 'victim.txt', 'text/plain')},
                     content_type='multipart/form-data')
    assert rv.status_code == 302
    return rv.headers['Location'].split('#')[0].rstrip('/').split('/')[-1]


def upload_new(client, size):
    rv = client.post('/+upload/new?token=creator',
                     json={'filename': 'new.bin', 'size': size, 'type': 'application/octet-stream',
                           'maxlife_unit': 'FOREVER', 'maxlife_value': 1})
    assert rv.status_code == 200
    return rv.get_json()['name']


def continue_upload(client, name, data, content_range=None):
    headers = {'Content-Range': content_range} if content_range else {}
    return client.post(f'/+upload/{name}?token=creator', headers=headers,
                       data={'file': (io.BytesIO(data), 'x.bin')}, content_type='multipart/form-data')


def rest_continue(client, name, data, begin, total, end=None):
    payload = base64.b64encode(data)
    if end is None:
        end = begin + len(data) - 1
    headers = {
        'Content-Length': str(len(payload)),
        'Content-Range': f'bytes {begin}-{end}/{total}',
        'Transaction-ID': base64.b64encode(name.encode()).decode(),
    }
    return client.post('/apis/rest/items?token=creator', headers=headers, data=payload)


def read_item(app, name):
    with app.app_context():
        with app.storage.open(name) as item:
            return item.data.read(item.data.size, 0), dict(item.meta)


@pytest.mark.parametrize('locked', [False, True])
def test_web_continue_rejects_complete_item(app, client, locked):
    name = upload_complete(client)
    if locked:
        assert client.post(f'/{name}/+lock?token=admin').status_code == 302
    for content_range in [None, 'bytes 0-3/16']:
        rv = continue_upload(client, name, b'EVIL', content_range)
        assert rv.status_code == 409
    data, meta = read_item(app, name)
    assert data == b'original content'
    assert meta[LOCKED] is locked


@pytest.mark.parametrize('locked', [False, True])
def test_rest_continue_rejects_complete_item(app, client, locked):
    name = upload_complete(client, b'ORIG')
    if locked:
        assert client.post(f'/{name}/+lock?token=admin').status_code == 302
    rv = rest_continue(client, name, b'APPENDED', 4, 12)
    assert rv.status_code == 409
    data, _ = read_item(app, name)
    assert data == b'ORIG'


def test_web_continue_chunked(app, client):
    name = upload_new(client, 10)
    assert continue_upload(client, name, b'01234', 'bytes 0-4/10').status_code == 200
    assert continue_upload(client, name, b'56789', 'bytes 5-9/10').status_code == 200
    data, meta = read_item(app, name)
    assert data == b'0123456789'
    assert meta[COMPLETE] and meta[SIZE] == 10
    # the upload is complete now, so no more writes are accepted
    assert continue_upload(client, name, b'X', 'bytes 0-0/10').status_code == 409


def test_web_continue_single(app, client):
    name = upload_new(client, 4)
    assert continue_upload(client, name, b'data').status_code == 200
    data, meta = read_item(app, name)
    assert data == b'data'
    assert meta[COMPLETE]


@pytest.mark.parametrize('data, content_range', [
    (b'Z', 'bytes 1000000000000-1000000000000/1000000000001'),  # far beyond the declared size
    (b'Z', 'bytes 10-10/11'),  # just beyond the declared size
    (b'too long', None),  # unchunked upload not matching the declared size
])
def test_web_continue_must_match_declared_size(app, client, data, content_range):
    name = upload_new(client, 10)
    rv = continue_upload(client, name, data, content_range)
    assert rv.status_code == 400
    data, meta = read_item(app, name)
    assert data == b''
    assert not meta[COMPLETE]


def test_web_continue_missing_item(client):
    assert continue_upload(client, 'abcdefgh', b'x').status_code == 404


@pytest.mark.parametrize('name', ['invalid', '..', 'abcdefgh.x', 'abc\\defgh'])
def test_rest_continue_rejects_invalid_names(client, name):
    assert rest_continue(client, name, b'x', 0, 1).status_code == 400


def test_rest_continue_total_size_limit(app, client):
    app.config['MAX_ALLOWED_FILE_SIZE'] = 10
    payload = b'0123456789'
    headers = {
        'Content-Length': str(len(base64.b64encode(payload))),
        'Content-Range': 'bytes 0-9/11',
    }
    rv = client.post('/apis/rest/items?token=creator', headers=headers, data=base64.b64encode(payload))
    assert rv.status_code == 413


def test_rest_continue_real_size_limit(app, client):
    # The limit must hold for the data that is really sent, whatever Content-Range says.
    app.config['MAX_ALLOWED_FILE_SIZE'] = 100
    chunk = b'x' * 70
    payload = base64.b64encode(chunk)
    headers = {'Content-Length': str(len(payload)), 'Content-Range': 'bytes 0-69/100'}
    rv = client.post('/apis/rest/items?token=creator', headers=headers, data=payload)
    assert rv.status_code == 200
    name = base64.b64decode(rv.headers['Transaction-ID']).decode()
    # the 2nd chunk announces 30 bytes, but sends 70 (140 bytes in total):
    assert rest_continue(client, name, chunk, 70, 100, end=99).status_code == 413
    data, meta = read_item(app, name)
    assert data == chunk
    assert not meta[COMPLETE]
    # a 2nd chunk that fits completes the upload:
    assert rest_continue(client, name, b'y' * 30, 70, 100).status_code == 201
    data, meta = read_item(app, name)
    assert data == chunk + b'y' * 30
    assert meta[COMPLETE] and meta[SIZE] == 100
