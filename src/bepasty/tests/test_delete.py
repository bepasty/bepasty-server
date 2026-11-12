#
# Deleting items via the web UI
#

import pytest

from ..app import create_app
from ..config import Config


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, 'STORAGE_FILESYSTEM_DIRECTORY', str(tmp_path))
    monkeypatch.setattr(Config, 'SECRET_KEY', 'secret')
    monkeypatch.setattr(Config, 'DEFAULT_PERMISSIONS', '')
    monkeypatch.setattr(Config, 'PERMISSIONS', {
        'admin': 'admin,list,create,modify,read,delete',
        'user': 'create,read,delete',
    })
    monkeypatch.delenv('BEPASTY_CONFIG', raising=False)
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def incomplete(client):
    # an upload in progress: created, but no data sent yet
    rv = client.post('/+upload/new?token=user', json={'filename': 'f.bin', 'size': 10, 'type': 'x/y',
                                                      'maxlife_unit': 'FOREVER', 'maxlife_value': 1})
    assert rv.status_code == 200
    return rv.get_json()['name']


def exists(app, name):
    with app.app_context():
        return name in app.storage


def test_delete_incomplete_needs_admin(app, client, incomplete):
    rv = client.post(f'/{incomplete}/+delete?token=user')
    assert rv.status_code == 409
    assert b'Upload incomplete' in rv.data
    assert exists(app, incomplete)


def test_delete_incomplete_as_admin(app, client, incomplete):
    rv = client.post(f'/{incomplete}/+delete?token=admin')
    assert rv.status_code == 302
    assert not exists(app, incomplete)


def test_delete_complete(app, client):
    rv = client.post('/+upload?token=user',
                     data={'text': 'hello', 'contenttype': 'text/plain', 'filename': 'a.txt'})
    assert rv.status_code == 302
    name = rv.headers['Location'].split('#')[0].rstrip('/').split('/')[-1]
    rv = client.post(f'/{name}/+delete?token=user')
    assert rv.status_code == 302
    assert not exists(app, name)
