from flask import Blueprint, current_app, jsonify
from flask.views import MethodView

blueprint = Blueprint('bepasty_apis', __name__, url_prefix='/apis')

from . import (
    lodgeit, rest)
