from flask import Blueprint

blueprint = Blueprint('bepasty_apis', __name__, url_prefix='/apis')

from . import (
    lodgeit, rest)
