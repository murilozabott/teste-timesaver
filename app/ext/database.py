from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DB_URL"]
    db.init_app(app)

    # Só modelos importados são registrados para geração de migrations
    # Garante que todos foram regisrados (temporário)
    from app import models  # noqa: F401
