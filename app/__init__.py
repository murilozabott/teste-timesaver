from flask import Flask

from app.ext import configuration


def create_app():
    app = Flask(__name__)
    configuration.init_app(app)

    @app.route("/")
    # check if dynaconf and sql alchemy extension were configured properly
    def test():
        from flask import jsonify
        from sqlalchemy import text

        from app.ext.database import db

        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception as e:
            return jsonify(
                {"status": "error", "database": "not connected", "details": repr(e)}
            ), 500

    return app
