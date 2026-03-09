from flask import request
from flask_restful import Resource

from app.blueprints.api.auth import require_role
from app.blueprints.api.schemas import DoctorCreate
from app.ext.database import db
from app.models import Doctor
from app.models.user import UserRole


class DoctorList(Resource):
    def get(self):
        """Público - qualquer um pode listar médicos"""
        doctors = Doctor.query.all()
        return [
            {
                "id": d.id,
                "name": d.name,
                "specialty": d.specialty,
                "crm": d.crm,
            }
            for d in doctors
        ]

    @require_role(UserRole.ADMIN)
    def post(self):
        data = DoctorCreate.model_validate(request.get_json())
        doctor = Doctor(
            name=data.name,
            specialty=data.specialty,
            crm=data.crm,
        )
        db.session.add(doctor)
        db.session.commit()
        return {
            "id": doctor.id,
            "name": doctor.name,
            "specialty": doctor.specialty,
            "crm": doctor.crm,
        }, 201


class DoctorDetail(Resource):
    def get(self, crm):
        """Público - qualquer um pode ver detalhes de médico"""
        doctor = db.session.query(Doctor).filter_by(crm=crm).first()
        if not doctor:
            return {"message": "Doctor not found"}, 404
        return {
            "id": doctor.id,
            "name": doctor.name,
            "specialty": doctor.specialty,
            "crm": doctor.crm,
        }

    @require_role(UserRole.ADMIN)
    def delete(self, crm):
        doctor = db.session.query(Doctor).filter_by(crm=crm).first()
        if not doctor:
            return {"message": "Doctor not found"}, 404
        db.session.delete(doctor)
        db.session.commit()
        return "", 204
