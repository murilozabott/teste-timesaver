from flask import Flask

from app.ext import configuration


def create_app():
    app = Flask(__name__, static_folder=None)
    configuration.init_app(app)

    return app
