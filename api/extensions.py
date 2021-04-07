from flask import Flask, current_app
from flask_pymongo import PyMongo

from api.publisher import Publisher

pymongo = PyMongo()
pub = Publisher()

def register_extensions(app: Flask):
    pymongo.init_app(app)

    #@app.before_first_request
    def start_publisher():
        pub.start()

    start_publisher()