import pytest

from .upload import ContentRange

def test_ContentRange_parse():
    r = ContentRange.parse('bytes 0-1/2')
    assert r.begin == 0
    assert r.end == 1
    assert r.complete == 2
    assert r.size == 2

    with pytest.raises(RuntimeError):
        ContentRange.parse('test 0-1/2')

    with pytest.raises(RuntimeError):
        ContentRange.parse('bytes 1-0/2')

    with pytest.raises(RuntimeError):
        ContentRange.parse('bytes 0-2/2')
