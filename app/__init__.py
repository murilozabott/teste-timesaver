from flask import Flask

from app.ext import configuration


def create_app():
    app = Flask(__name__)
    configuration.init_app(app)

    @app.route("/")
    def test():
        """
        Rota básica de "healthcheck"
        """

        from flask import jsonify
        from sqlalchemy import text

        from app.ext.database import db
        from app.models.user import User, UserRole

        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "database": "connected"}), 200
        except Exception as e:
            return jsonify(
                {"status": "error", "database": "not connected", "details": repr(e)}
            ), 500

    return app
