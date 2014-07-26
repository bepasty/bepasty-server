# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from flask import Blueprint

blueprint = Blueprint('bepasty', __name__)

from . import (
    index,
    xstatic,
    filelist,
    display,
    download,
    upload,
    setkv,
    delete,
    login)
