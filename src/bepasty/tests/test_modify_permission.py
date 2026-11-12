#
# Modifying item metadata requires the "modify" permission
#

import io

import pytest

from ..app import create_app
from ..config import Config
from ..constants import FILENAME, TYPE


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, 'STORAGE_FILESYSTEM_DIRECTORY', str(tmp_path))
    monkeypatch.setattr(Config, 'SECRET_KEY', 'secret')
    monkeypatch.setattr(Config, 'DEFAULT_PERMISSIONS', '')
    monkeypatch.setattr(Config, 'PERMISSIONS', {
        'admin': 'admin,list,create,modify,read,delete',
        'creator': 'create,read',
        'modifier': 'modify,read',
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
def name(client):
    rv = client.post('/+upload?token=admin', data={'file': (io.BytesIO(b'content'), 'orig.txt', 'text/plain')},
                     content_type='multipart/form-data')
    assert rv.status_code == 302
    return rv.headers['Location'].split('#')[0].rstrip('/').split('/')[-1]


def get_meta(app, name):
    with app.app_context():
        with app.storage.open(name) as item:
            return item.meta[FILENAME], item.meta[TYPE]


def modify_web(client, name, token):
    return client.post(f'/{name}/+modify?token={token}', data={'filename': 'new.txt', 'contenttype': 'text/x-python'})


def modify_rest(client, name, token):
    return client.post(f'/apis/rest/items/{name}/modify?token={token}',
                       json={'filename': 'new.txt', 'type': 'text/x-python'})


@pytest.mark.parametrize('modify', [modify_web, modify_rest])
def test_create_permission_is_not_enough(app, client, name, modify):
    assert modify(client, name, 'creator').status_code == 403
    assert get_meta(app, name) == ('orig.txt', 'text/plain')


@pytest.mark.parametrize('modify, status', [(modify_web, 302), (modify_rest, 200)])
def test_modify_permission_is_enough(app, client, name, modify, status):
    assert modify(client, name, 'modifier').status_code == status
    assert get_meta(app, name) == ('new.txt', 'text/x-python')


def test_modify_button_shown_only_with_modify_permission(client, name):
    assert b'id="modify-btn"' in client.get(f'/{name}?token=modifier').data
    assert b'id="modify-btn"' not in client.get(f'/{name}?token=creator').data
