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
