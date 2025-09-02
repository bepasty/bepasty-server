import re
import random

from werkzeug.routing import BaseConverter

ID_LENGTH = 8

letters_lower = set("abcdefghijklmnopqrstuvwxyz")
letters_upper = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
digits = set("0123456789")

# Characters that might be hard to read/differentiate or are otherwise unwanted:
unwanted = set(
    "1lI"
    "0O"
    "8B"
    "5S"
    "+"  # used in URL dispatching for views, e.g., +login
    "/"  # used in URLs and filesystem paths
)

all_chars = letters_lower | letters_upper | digits
all_chars -= unwanted
all_chars = ''.join(sorted(all_chars))


def encode(x, length, alphabet=all_chars):
    """
    Encode x in the given alphabet (with leading zeroes).

    :param x: integer number
    :param length: length of the returned sequence
    :param alphabet: alphabet to choose characters from (default: all_chars)
    :return: sequence of alphabet members [list]
    """
    if x < 0:
        raise ValueError("Negative values are not supported")
    if length < 0:
        raise ValueError("Length must be >= 0")
    n = len(alphabet)
    if n < 2:
        raise ValueError("Alphabet must be at least 2 elements long")
    code = []
    counter = length
    while x > 0 and counter > 0:
        x, r = divmod(x, n)
        code.append(alphabet[r])
        counter -= 1
    leading_zeroes = length - len(code)
    code += list(alphabet[0] * leading_zeroes)
    return list(reversed(code))


def make_id(length, x=None, alphabet=all_chars):
    """
    Generate an ID of <length> from value <x>.
    If x is None, use a random value for x.
    For the ID, use elements from the given alphabet.
    """
    base = len(alphabet)  # e.g. 10
    if x is None:
        x = random.randint(
            0,                  # 000 (length == 3) ...
            base ** length - 1  # 999 (length == 3)
        )
    return ''.join(encode(x, length, alphabet))


class ItemName(str):
    def __new__(cls, uid):
        return str(uid)

    @classmethod
    def create(cls, storage, length=ID_LENGTH, max_length=2 * ID_LENGTH, max_tries=10):
        """
        Create a unique item name in storage; desired name length is <length>.

        We try at most <max_tries> times to find a unique name of a specific length.
        If we do not succeed, we increase the name length and try again.
        If we can't find a unique name even for longer lengths up to max_length,
        we'll raise RuntimeError.
        """
        name = None  # avoid false alarm about reference before assignment
        while length <= max_length:
            tries = 0
            while tries < max_tries:
                name = make_id(length)
                if name not in storage:
                    break
                tries += 1
            if tries < max_tries:
                # we found a name, break out of outer while also
                break
            length += 1
        if length > max_length:
            raise RuntimeError("No unique names available")
        return cls(name)


class ItemNameConverter(BaseConverter):
    """
    Accept names in the same style as we generate.
    """
    # For a while, support both old UUID4-style as well as new shorter IDs
    regex = (
        '([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})'
        '|'
        '([%(valid)s]{%(length)d})'
    ) % dict(valid=re.escape(all_chars), length=ID_LENGTH)
    weight = 200


def setup_werkzeug_routing(app):
    app.url_map.converters['itemname'] = ItemNameConverter
