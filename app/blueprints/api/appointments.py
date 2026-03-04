from flask import request
from flask_restful import Resource

from app.blueprints.api.schemas import AppointmentCreate, AppointmentUpdate
from app.models import Appointment
from app.services import AppointmentService


def serialize_appointment(appointment: Appointment) -> dict:
    return {
        "id": appointment.id,
        "doctor_id": appointment.doctor_id,
        "patient_id": appointment.patient_id,
        "scheduled_at": appointment.scheduled_at.isoformat(),
        "status": appointment.status.value,
        "notes": appointment.notes,
    }


class AppointmentList(Resource):
    def get(self):
        appointments = AppointmentService.list_appointments()
        return [serialize_appointment(a) for a in appointments]

    def post(self):
        data = AppointmentCreate.model_validate(request.get_json())

        appointment = AppointmentService.create_appointment(
            doctor_id=data.doctor_id,
            patient_id=data.patient_id,
            scheduled_at=data.scheduled_at,
            notes=data.notes,
        )

        return serialize_appointment(appointment), 201


class AppointmentDetail(Resource):
    def get(self, id):
        appointment = AppointmentService.get_appointment(id)
        return serialize_appointment(appointment)

    def put(self, id):
        data = AppointmentUpdate.model_validate(request.get_json())

        appointment = AppointmentService.update_appointment(
            appointment_id=id,
            doctor_id=data.doctor_id,
            patient_id=data.patient_id,
            scheduled_at=data.scheduled_at,
            status=data.status,
            notes=data.notes,
        )

        return serialize_appointment(appointment)

    def delete(self, id):
        AppointmentService.delete_appointment(id)
        return "", 204
