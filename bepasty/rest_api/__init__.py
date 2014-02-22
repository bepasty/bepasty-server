# Copyright: 2014 Dennis Schmalacker <github@progde.de>
# License: BSD 2-clause, see LICENSE for details.

from flask import Blueprint

rest_api = Blueprint('bepasty_rest', __name__, url_prefix='/api/v1')

from . import (
    items)