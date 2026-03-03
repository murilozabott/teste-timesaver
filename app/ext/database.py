from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DB_URL"]
    db.init_app(app)
