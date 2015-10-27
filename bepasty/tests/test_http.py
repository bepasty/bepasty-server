import pytest
from werkzeug.exceptions import BadRequest

from bepasty.utils.http import ContentRange


def test_contentrange_parse():
    r = ContentRange.parse('bytes 0-0/2')
    assert r.begin == 0
    assert r.end == 0
    assert r.complete == 2
    assert r.size == 1
    assert not r.is_complete

    r = ContentRange.parse('bytes 0-1/2')
    assert r.begin == 0
    assert r.end == 1
    assert r.complete == 2
    assert r.size == 2
    assert r.is_complete

    with pytest.raises(BadRequest):
        ContentRange.parse('test 0-1/2')

    with pytest.raises(BadRequest):
        ContentRange.parse('bytes 1-0/2')

    with pytest.raises(BadRequest):
        ContentRange.parse('bytes 0-2/2')
