#
# Content-Security-Policy on responses that the browser renders directly
#

import io

import pytest

from ..app import create_app
from ..config import Config
from ..views.download import INLINE_CSP

SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>'


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


def upload(client, data, filename, content_type):
    rv = client.post('/+upload', data={'file': (io.BytesIO(data), filename, content_type)},
                     content_type='multipart/form-data')
    assert rv.status_code == 302
    # Location is like /<name>/#<filename>
    return rv.headers['Location'].split('#')[0].rstrip('/').split('/')[-1]


def test_inline_csp_policy():
    # the essential properties of the policy:
    directives = [d.strip() for d in INLINE_CSP.split(';')]
    sandbox = [d for d in directives if d.startswith('sandbox')]
    assert len(sandbox) == 1
    assert 'allow-scripts' not in sandbox[0]  # this is what stops script execution
    assert "default-src 'none'" in directives
    assert not any(d.startswith('script-src') for d in directives)


@pytest.mark.parametrize('filename, content_type, data', [
    ('image.svg', 'image/svg+xml', SVG),
    ('page.xhtml', 'application/xhtml+xml', b'<html xmlns="http://www.w3.org/1999/xhtml"/>'),
    ('page.html', 'text/html', b'<html></html>'),
    ('image.png', 'image/png', b'not really a png'),
    ('audio.mp3', 'audio/mpeg', b'not really an mp3'),
    ('video.mp4', 'video/mp4', b'not really an mp4'),
    ('doc.pdf', 'application/pdf', b'%PDF-1.4 not really a pdf'),
    ('text.txt', 'text/plain', b'hello'),
])
def test_inline_has_csp(client, filename, content_type, data):
    name = upload(client, data, filename, content_type)
    rv = client.get(f'/{name}/+inline')
    assert rv.status_code == 200
    assert rv.headers['Content-Disposition'].startswith('inline;')
    assert rv.headers['Content-Security-Policy'] == INLINE_CSP
    assert rv.headers['X-Content-Type-Options'] == 'nosniff'
    assert rv.data == data


@pytest.mark.parametrize('content_type', [
    'text/html',
    'Text/HTML',  # content types are case-insensitive
    'text/xml',
    'text/x-python',
    'application/xml',
    'application/xhtml+xml',
    'Application/XHTML+XML',
    'application/atom+xml',
    'application/mathml+xml',
    'multipart/x-mixed-replace',
])
def test_inline_documents_are_sent_as_plain_text(client, content_type):
    # the browser shall show the source, not render it as a page of our site
    data = b'<html xmlns="http://www.w3.org/1999/xhtml"><body>hello</body></html>'
    name = upload(client, data, 'page.bin', content_type)
    rv = client.get(f'/{name}/+inline')
    assert rv.status_code == 200
    assert rv.headers['Content-Type'] == 'text/plain'
    assert rv.headers['Content-Security-Policy'] == INLINE_CSP
    assert rv.data == data


@pytest.mark.parametrize('content_type', [
    'image/svg+xml',  # needs its type to display as an image, the CSP stops its scripts
    'image/png',
    'audio/mpeg',
    'video/mp4',
    'application/pdf',
    'application/octet-stream',
])
def test_inline_other_types_keep_their_type(client, content_type):
    name = upload(client, SVG, 'file.bin', content_type)
    rv = client.get(f'/{name}/+inline')
    assert rv.status_code == 200
    assert rv.headers['Content-Type'] == content_type
    assert rv.headers['Content-Security-Policy'] == INLINE_CSP


def test_download_keeps_document_type(client):
    name = upload(client, b'<html></html>', 'page.html', 'text/html')
    rv = client.get(f'/{name}/+download')
    assert rv.headers['Content-Disposition'].startswith('attachment;')
    assert rv.headers['Content-Type'].startswith('text/html')


def test_download_has_no_csp(client):
    name = upload(client, SVG, 'image.svg', 'image/svg+xml')
    rv = client.get(f'/{name}/+download')
    assert rv.status_code == 200
    assert rv.headers['Content-Disposition'].startswith('attachment;')
    assert 'Content-Security-Policy' not in rv.headers
    assert rv.headers['X-Content-Type-Options'] == 'nosniff'


def test_thumbnail_placeholder_has_csp(client):
    # an SVG item gets the placeholder thumbnail (also an SVG)
    name = upload(client, SVG, 'image.svg', 'image/svg+xml')
    rv = client.get(f'/{name}/+thumbnail')
    assert rv.status_code == 200
    assert rv.headers['Content-Type'] == 'image/svg+xml'
    assert rv.headers['Content-Security-Policy'] == INLINE_CSP
    assert rv.headers['X-Content-Type-Options'] == 'nosniff'
