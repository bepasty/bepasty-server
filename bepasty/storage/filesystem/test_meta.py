import tempfile

from . import Meta

def test():
    f = tempfile.TemporaryFile()

    m = Meta(f)
    assert len(m) == 0

    m['flag'] = True
    m.flush()
