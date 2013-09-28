import pytest

from .upload import Upload

def test_Upload_range():
    r = Upload._range('bytes 0-1/2')
    assert r[0] == 0
    assert r[1] == 1
    assert r[2] == 2

    with pytest.raises(RuntimeError):
        Upload._range('test 0-1/2')

    with pytest.raises(RuntimeError):
        Upload._range('bytes 1-0/2')

    with pytest.raises(RuntimeError):
        Upload._range('bytes 0-2/2')
