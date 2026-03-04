from flask import jsonify
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest


def register_error_handlers(app):
    """
    Configurar gerenciamento global de erros para evitar necessidade
    de try/except em cada função
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify(
            {
                "message": "Validation error",
                "errors": error.errors(),
            }
        ), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        return jsonify({"message": "Database integrity error"}), 409

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify({"message": "Invalid JSON body"}), 400

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return jsonify({"message": "Internal server error"}), 500
