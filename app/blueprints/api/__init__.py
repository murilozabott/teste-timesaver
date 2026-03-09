from flask import Blueprint
from flask_restful import Api

from app.blueprints.api.appointments import AppointmentDetail, AppointmentList
from app.blueprints.api.auth import LoginResource, RegisterResource
from app.blueprints.api.doctors import DoctorDetail, DoctorList
from app.blueprints.api.errors import register_error_handlers
from app.blueprints.api.patients import PatientDetail, PatientList

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

api.add_resource(RegisterResource, "/auth/register")
api.add_resource(LoginResource, "/auth/login")

api.add_resource(DoctorList, "/doctors")
api.add_resource(DoctorDetail, "/doctors/<string:crm>")

api.add_resource(PatientList, "/patients")
# API Query por ID com ID serial não é exatamente ideal
# algo como UUID seria mais adequado, mantido assim por simplicidade
api.add_resource(PatientDetail, "/patients/<int:id>")

api.add_resource(AppointmentList, "/appointments")
api.add_resource(AppointmentDetail, "/appointments/<int:id>")


def init_app(app):
    register_error_handlers(app)
    app.register_blueprint(api_bp, url_prefix="/api/v1")
