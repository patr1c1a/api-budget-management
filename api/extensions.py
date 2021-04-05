from flask import Flask
from flask_pymongo import PyMongo

pymongo = PyMongo()


def register_extensions(app: Flask):
    pymongo.init_app(app)

