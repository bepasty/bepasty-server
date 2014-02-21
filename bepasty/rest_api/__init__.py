from flask.ext.restful import Api
from flask import current_app

api = Api(app=current_app, prefix='/api/v1')

