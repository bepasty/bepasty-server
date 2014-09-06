# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import re
import random

from werkzeug.routing import BaseConverter

ID_LENGTH = 8

letters_lower = set("abcdefghijklmnopqrstuvwxyz")
letters_upper = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
digits = set("0123456789")

# this stuff might be hard to read / differentiate or is otherwise unwanted:
unwanted = set("1lI"
               "0O"
               "8B"
               "5S"
               '+'  # used in URL dispatching for views, e.g. +login
               '/'  # used in URLs and fs paths
              )

all_chars = letters_lower | letters_upper | digits
all_chars -= unwanted
all_chars = ''.join(sorted(all_chars))


def encode(x, length, alphabet=all_chars):
    """
    encode x in alphabet (with "leading zeroes")

    :param x: integer number
    :param length: length of return sequence
    :return: sequence of alphabet members [list]
    """
    if x < 0:
        raise ValueError("negative values are not supported")
    if length < 0:
        raise ValueError("length must be >= 0")
    n = len(alphabet)
    if n < 2:
        raise ValueError("alphabet must be at least 2 elements long")
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
    generate a id of <length> from value <x>.
    if x is None, use a random value for x.
    for the id, use elements from alphabet.
    """
    base = len(alphabet)  # e.g. 10
    if x is None:
        x = random.randint(0,                  # 000 (length==3) ...
                           base ** length - 1  # 999 (length==3)
                          )
    return ''.join(encode(x, length, alphabet))


class ItemName(str):
    def __new__(cls, uid):
        return str(uid)

    @classmethod
    def create(cls, length=ID_LENGTH):
        return cls(make_id(length))


class ItemNameConverter(BaseConverter):
    """
    Accept the names of the style as we generate.
    """
    # for a while, support both old uuid4-style as well as new shorter IDs
    regex = ('([a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12})'
             '|'
             '([%(valid)s]{%(length)d})'
            ) % dict(valid=re.escape(all_chars), length=ID_LENGTH)
    weight = 200


def setup_werkzeug_routing(app):
    app.url_map.converters['itemname'] = ItemNameConverter
