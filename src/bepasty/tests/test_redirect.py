#
# tests for the text/x-bepasty-redirect item type
#

from io import BytesIO

import pytest

from ..app import create_app
from ..config import Config
from ..utils.http import is_safe_external_url
from ..utils.upload import create_item
from ..views.display import DEFAULT_REDIRECT_DELAY, parse_delay

REDIRECT_TYPE = 'text/x-bepasty-redirect'


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, 'STORAGE_FILESYSTEM_DIRECTORY', str(tmp_path))
    monkeypatch.setattr(Config, 'DEFAULT_PERMISSIONS', 'create,read')
    monkeypatch.setattr(Config, 'PERMISSIONS', {})
    app = create_app()
    app.config['TESTING'] = True
    return app


def store_redirect(app, url):
    """store a redirect item directly, bypassing upload-time validation"""
    data = url.encode('utf-8')
    with app.test_request_context():
        return create_item(BytesIO(data), 'link', len(data), REDIRECT_TYPE, 'text/plain')


@pytest.mark.parametrize('url', [
    'http://example.org/',
    'https://example.org/path?q=1#frag',
    'HTTPS://EXAMPLE.ORG',
    '  https://example.org/  ',
])
def test_safe_urls(url):
    assert is_safe_external_url(url)


@pytest.mark.parametrize('url', [
    'javascript:alert(1)',
    'JavaScript:alert(1)',
    ' javascript:alert(1)',
    '\x00javascript:alert(1)',
    'java\tscript:alert(1)',
    'java\nscript:alert(1)',
    'data:text/html,<script>alert(1)</script>',
    'vbscript:msgbox(1)',
    'file:///etc/passwd',
    '//evil.example/',
    '/relative/path',
    'https://',
    'https:evil.example',
    'http://[::1',
    '',
])
def test_unsafe_urls(url):
    assert not is_safe_external_url(url)


@pytest.mark.parametrize('value, expected', [
    (None, DEFAULT_REDIRECT_DELAY),
    ('', DEFAULT_REDIRECT_DELAY),
    ('0', 0),
    ('5', 5),
    ('9999', 9999),
    ('-1', DEFAULT_REDIRECT_DELAY),
    ('abc', DEFAULT_REDIRECT_DELAY),
    ('1.5', DEFAULT_REDIRECT_DELAY),
    ('0;url=https://evil.example/', DEFAULT_REDIRECT_DELAY),
])
def test_parse_delay(value, expected):
    assert parse_delay(value) == expected


def test_redirect_display(app):
    name = store_redirect(app, 'https://example.org/target')
    rv = app.test_client().get(f'/{name}')
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert 'content="3; url=https://example.org/target"' in body
    assert '<a href="https://example.org/target">' in body


def test_redirect_delay_injection(app):
    name = store_redirect(app, 'https://example.org/target')
    rv = app.test_client().get(f'/{name}', query_string={'delay': '0;url=https://evil.example/'})
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert 'evil.example' not in body
    assert 'content="3; url=https://example.org/target"' in body


def test_redirect_display_unsafe_stored_url(app):
    # items created before upload-time validation existed must not be rendered as a link
    name = store_redirect(app, 'javascript:alert(document.domain)')
    rv = app.test_client().get(f'/{name}')
    assert rv.status_code == 200
    body = rv.get_data(as_text=True)
    assert 'http-equiv="refresh"' not in body
    assert 'href="javascript:' not in body
    assert 'Invalid redirect URL' in body


def test_redirect_upload(app):
    client = app.test_client()
    form = {'filename': 'link', 'contenttype': REDIRECT_TYPE}
    rv = client.post('/+upload', data=dict(form, text='https://example.org/'))
    assert rv.status_code == 302
    rv = client.post('/+upload', data=dict(form, text='javascript:alert(1)'))
    assert rv.status_code == 400
