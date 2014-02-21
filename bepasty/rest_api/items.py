from . import api
from flask.ext.restful import Resource

class Item(Resource):
	def get(self):
		return 'Hello World'

api.add_ressource(Item, '/items')

