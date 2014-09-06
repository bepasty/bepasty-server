from . import Data


def test(tmpdir):
    p = tmpdir.join("test.data")

    d = Data(p.open('w+b'))
    assert d.size == 0

    d.write('a' * 1024, 0)
    assert d.size == 1024

    d.write('a' * 1024, 1024 * 3)
    assert d.size == 1024 * 4

    assert d.read(1024, 0) == 'a' * 1024
    assert d.read(1024, 1024) == '\0' * 1024

    d.close()
