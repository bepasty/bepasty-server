#
# Running behind a reverse proxy (PROXY_FIX)
#

import pytest

from ..app import create_app
from ..config import Config

HEADERS = {'X-Forwarded-Proto': 'https', 'X-Forwarded-Host': 'paste.example.org'}


def make_client(tmp_path, monkeypatch, proxy_fix):
    monkeypatch.setattr(Config, 'STORAGE_FILESYSTEM_DIRECTORY', str(tmp_path))
    monkeypatch.setattr(Config, 'SECRET_KEY', 'secret')
    monkeypatch.setattr(Config, 'PROXY_FIX', proxy_fix)
    monkeypatch.delenv('BEPASTY_CONFIG', raising=False)
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()


def qr_target(client):
    # the QR code view renders an absolute URL of the item
    html = client.get('/abcdefgh/+qr', headers=HEADERS).get_data(as_text=True)
    start = html.index('value="http') + len('value="')
    return html[start:html.index('"', start)]


def test_no_proxy_fix(tmp_path, monkeypatch):
    # default: X-Forwarded-* headers are ignored (they could be faked by clients)
    client = make_client(tmp_path, monkeypatch, None)
    assert qr_target(client) == 'http://localhost/abcdefgh'


@pytest.mark.parametrize('proxy_fix, expected', [
    ({'x_proto': 1}, 'https://localhost/abcdefgh'),
    ({'x_proto': 1, 'x_host': 1}, 'https://paste.example.org/abcdefgh'),
])
def test_proxy_fix(tmp_path, monkeypatch, proxy_fix, expected):
    client = make_client(tmp_path, monkeypatch, proxy_fix)
    assert qr_target(client) == expected


def test_proxy_fix_with_app_base_path(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, 'APP_BASE_PATH', '/bepasty')
    client = make_client(tmp_path, monkeypatch, {'x_proto': 1})
    html = client.get('/bepasty/abcdefgh/+qr', headers=HEADERS).get_data(as_text=True)
    assert 'https://localhost/bepasty/abcdefgh' in html
