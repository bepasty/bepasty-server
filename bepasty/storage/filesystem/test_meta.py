import tempfile

from . import Meta

def test():
    f = tempfile.TemporaryFile()

    m = Meta(f)
    assert len(m) == 0
    m.write()

    m = Meta(f)
    m['flag'] = True
    assert len(m) == 1
    m.write()

    m = Meta(f)
    assert len(m) == 1
    assert m['flag'] is True
