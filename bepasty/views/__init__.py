from flask import Blueprint

blueprint = Blueprint('bepasty', __name__)

from . import (
        index,
        display,
        download,
        upload,
        )

