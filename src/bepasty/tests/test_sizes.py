#
# Displaying item sizes in the web UI
#

import pytest

from ..app import create_app
from ..config import Config


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, 'STORAGE_FILESYSTEM_DIRECTORY', str(tmp_path))
    monkeypatch.setattr(Config, 'SECRET_KEY', 'secret')
    monkeypatch.setattr(Config, 'DEFAULT_PERMISSIONS', 'admin,list,create,read')
    monkeypatch.delenv('BEPASTY_CONFIG', raising=False)
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def upload(client, text):
    rv = client.post('/+upload', data={'text': text, 'filename': 'f.txt', 'contenttype': 'text/plain'})
    assert rv.status_code == 302
    return rv.headers['Location'].split('#')[0].rsplit('/', 1)[-1]


SEP = '\u202f'  # narrow no-break space


@pytest.mark.parametrize('size, expected', [
    (0, '0'),
    (999, '999'),
    (1000, f'1{SEP}000'),
    (1234567, f'1{SEP}234{SEP}567'),
    (123456789, f'123{SEP}456{SEP}789'),
])
def test_size_filter(client, size, expected):
    assert client.application.jinja_env.filters['size'](size) == expected


def test_display_size(client):
    name = upload(client, 'x' * 1234567)
    rv = client.get(f'/{name}')
    assert f'Size: 1{SEP}234{SEP}567 bytes' in rv.get_data(as_text=True)


def test_list_size(client):
    upload(client, 'x' * 1234567)
    rv = client.get('/+list')
    assert f'1{SEP}234{SEP}567' in rv.get_data(as_text=True)
