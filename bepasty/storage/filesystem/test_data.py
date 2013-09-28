import tempfile

from . import Data

def test():
    f = tempfile.TemporaryFile()

    d = Data(f)
    assert d.size() == 0
