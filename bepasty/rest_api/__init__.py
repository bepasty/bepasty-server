from flask.ext.restful import Api

api = Api(prefix='/api/v1')

from . import items