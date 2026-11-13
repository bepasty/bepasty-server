#
# Uploading via the web form and the lodgeit API
#

import pytest

from ..app import create_app
from ..config import Config


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, 'STORAGE_FILESYSTEM_DIRECTORY', str(tmp_path))
    monkeypatch.setattr(Config, 'SECRET_KEY', 'secret')
    monkeypatch.setattr(Config, 'DEFAULT_PERMISSIONS', 'create,read')
    monkeypatch.delenv('BEPASTY_CONFIG', raising=False)
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_upload_text_with_filename(client):
    rv = client.post('/+upload', data={'text': 'x', 'filename': 'a b.txt'})
    assert rv.status_code == 302
    assert rv.headers['Location'].endswith('#a%20b.txt')


def test_upload_text_without_filename(client):
    # e.g. curl --data 'text=...' does not send a filename
    rv = client.post('/+upload', data={'text': 'x'})
    assert rv.status_code == 302
    assert '#' not in rv.headers['Location']


def test_lodgeit_upload(client):
    rv = client.post('/apis/lodgeit/', data={'code': 'x', 'language': 'text'})
    assert rv.status_code == 302
    assert client.get(rv.headers['Location']).status_code == 200
