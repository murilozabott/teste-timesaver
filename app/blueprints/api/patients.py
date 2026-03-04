from flask import request
from flask_restful import Resource

from app.blueprints.api.schemas import PatientCreate
from app.ext.database import db
from app.models import Patient


class PatientList(Resource):
    def get(self):
        patients = Patient.query.all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "email": p.email,
                "birth_date": p.birth_date.isoformat(),
            }
            for p in patients
        ]

    def post(self):
        data = PatientCreate.model_validate(request.get_json())
        patient = Patient(
            name=data.name,
            email=data.email,
            birth_date=data.birth_date,
        )
        db.session.add(patient)
        db.session.commit()
        return {
            "id": patient.id,
            "name": patient.name,
            "email": patient.email,
            "birth_date": patient.birth_date.isoformat(),
        }, 201


class PatientDetail(Resource):
    def get(self, id):
        patient = db.session.get(Patient, id)
        if not patient:
            return {"message": "Patient not found"}, 404
        return {
            "id": patient.id,
            "name": patient.name,
            "email": patient.email,
            "birth_date": patient.birth_date.isoformat(),
        }

    def delete(self, id):
        patient = db.session.get(Patient, id)
        if not patient:
            return {"message": "Patient not found"}, 404
        db.session.delete(patient)
        db.session.commit()
        return "", 204
