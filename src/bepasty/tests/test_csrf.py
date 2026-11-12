#
# Protection against cross-site request forgery (CSRF)
#

import base64
import io

import pytest

from ..app import create_app
from ..config import Config
from ..constants import LOCKED

HOST = 'bepasty.example.org'

CROSS_ORIGIN = [
    {'Sec-Fetch-Site': 'cross-site'},
    {'Sec-Fetch-Site': 'same-site'},  # e.g. from a subdomain
    {'Sec-Fetch-Site': 'cross-site', 'Origin': f'https://{HOST}'},  # Sec-Fetch-Site wins
    {'Origin': 'https://evil.example'},  # older browsers only send Origin
    {'Origin': f'https://{HOST}.evil.example'},
    {'Origin': 'null'},  # e.g. from a sandboxed iframe or data: URL
]

SAME_ORIGIN = [
    {},  # non-browser clients send neither header
    {'Sec-Fetch-Site': 'same-origin'},
    {'Sec-Fetch-Site': 'none'},  # triggered by the user directly
    {'Sec-Fetch-Site': 'same-origin', 'Origin': f'https://{HOST}'},
    {'Origin': f'https://{HOST}'},
    {'Origin': f'https://{HOST.upper()}'},
]


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, 'STORAGE_FILESYSTEM_DIRECTORY', str(tmp_path))
    monkeypatch.setattr(Config, 'SECRET_KEY', 'secret')
    monkeypatch.setattr(Config, 'DEFAULT_PERMISSIONS', '')
    monkeypatch.setattr(Config, 'PERMISSIONS', {'admin': 'admin,list,create,modify,read,delete'})
    monkeypatch.delenv('BEPASTY_CONFIG', raising=False)
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


def base_url():
    return f'https://{HOST}'


def login(client, headers=None):
    return client.post('/+login', data={'token': 'admin'}, headers=headers or {}, base_url=base_url())


def upload(client, headers=None):
    return client.post('/+upload', data={'file': (io.BytesIO(b'content'), 'a.txt', 'text/plain')},
                       content_type='multipart/form-data', headers=headers or {}, base_url=base_url())


@pytest.fixture
def name(client):
    assert login(client).status_code == 302
    rv = upload(client)
    assert rv.status_code == 302
    return rv.headers['Location'].split('#')[0].rstrip('/').split('/')[-1]


def item_exists(app, name):
    with app.app_context():
        return name in app.storage


def is_locked(app, name):
    with app.app_context():
        with app.storage.open(name) as item:
            return item.meta[LOCKED]


@pytest.mark.parametrize('headers', CROSS_ORIGIN)
def test_cross_origin_rejected(app, client, name, headers):
    # the victim is logged in (session cookie), the attacker's page sends these:
    requests = [
        ('/+login', {'token': 'admin'}),
        ('/+logout', {}),
        ('/+upload', {'text': 'csrf', 'contenttype': 'text/plain', 'filename': 'x.txt'}),
        ('/+upload/new', None),
        (f'/{name}/+modify', {'filename': 'csrf.txt'}),
        (f'/{name}/+lock', {}),
        (f'/{name}/+unlock', {}),
        (f'/{name}/+delete', {}),
        (f'/+upload/{name}/abort', {}),
        ('/apis/lodgeit/', {'code': 'csrf'}),
        ('/apis/rest/items', None),
        (f'/apis/rest/items/{name}/delete', None),
    ]
    for url, data in requests:
        rv = client.post(url, data=data, headers=headers, base_url=base_url())
        assert rv.status_code == 403, url
    assert item_exists(app, name)
    assert not is_locked(app, name)
    # we are still logged in (logout was rejected, too):
    assert client.post(f'/{name}/+lock', base_url=base_url()).status_code == 302


@pytest.mark.parametrize('headers', CROSS_ORIGIN)
def test_cross_origin_basic_auth_rejected(app, client, headers):
    # browsers also send cached HTTP Basic auth credentials cross-site
    auth = 'Basic ' + base64.b64encode(b'user:admin').decode()
    rv = client.post('/+upload', data={'text': 'csrf', 'contenttype': 'text/plain', 'filename': 'x.txt'},
                     headers={**headers, 'Authorization': auth}, base_url=base_url())
    assert rv.status_code == 403


@pytest.mark.parametrize('headers', SAME_ORIGIN)
def test_same_origin_allowed(app, client, name, headers):
    rv = client.post(f'/{name}/+lock', headers=headers, base_url=base_url())
    assert rv.status_code == 302
    assert is_locked(app, name)
    rv = client.post(f'/{name}/+delete', headers=headers, base_url=base_url())
    assert rv.status_code == 302
    assert not item_exists(app, name)


@pytest.mark.parametrize('headers', CROSS_ORIGIN)
def test_cross_origin_get_allowed(client, name, headers):
    # safe methods are not affected, e.g. links from other sites keep working
    assert client.get(f'/{name}', headers=headers, base_url=base_url()).status_code == 200


def test_login_cross_origin_rejected(client):
    rv = login(client, {'Sec-Fetch-Site': 'cross-site'})
    assert rv.status_code == 403
    assert b'came from another site' in rv.data
    with client.session_transaction() as session:
        assert 'loggedin' not in session


def test_session_cookie_samesite(client):
    rv = login(client)
    assert 'SameSite=Lax' in rv.headers['Set-Cookie']


def test_upload_abort_needs_post(app, client):
    assert login(client).status_code == 302
    rv = client.post('/+upload/new', json={'filename': 'f', 'size': 10, 'type': 'x/y',
                                           'maxlife_unit': 'FOREVER', 'maxlife_value': 1},
                     base_url=base_url())
    name = rv.get_json()['name']
    assert client.get(f'/+upload/{name}/abort', base_url=base_url()).status_code == 405
    assert item_exists(app, name)
    assert client.post(f'/+upload/{name}/abort', base_url=base_url()).status_code == 200
    assert not item_exists(app, name)
