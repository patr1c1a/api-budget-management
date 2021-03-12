from flask import Flask
from flask_restful import Api
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_pyfile('../.env')
db = PyMongo(app).db
api = Api(app)

from api.controllers import OperationCollection, OperationResource

api.add_resource(OperationCollection, "/operations", endpoint="operations")
api.add_resource(OperationResource, "/operation", "/operation/<string:_id>", endpoint="operation")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
