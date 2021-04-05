from flask import Flask
from flask_restful import Api
from api.extensions import register_extensions
from api.routes import register_routes

app = Flask(__name__)
app.config.from_pyfile('../.env')
api = Api(app)
register_extensions(app)
register_routes(api)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
