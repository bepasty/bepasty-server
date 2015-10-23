from bepasty.storage.filesystem import Data


def test(tmpdir):
    p = tmpdir.join('test.data')

    d = Data(p.open('w+b'))
    assert d.size == 0

    d.write(b'a' * 1024, 0)
    assert d.size == 1024

    d.write(b'a' * 1024, 1024 * 3)
    assert d.size == 1024 * 4

    assert d.read(1024, 0) == b'a' * 1024
    assert d.read(1024, 1024) == b'\0' * 1024

    d.close()
