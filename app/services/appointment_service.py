from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app.exceptions import DoubleBookingError, EntityNotFoundError
from app.ext.database import db
from app.models import Appointment, Doctor, Patient
from app.models.appointment import AppointmentStatus


def _handle_integrity_error(exc: IntegrityError) -> None:
    """Converte erros de integridade do banco em exceções de domínio."""
    error_msg = str(exc.orig) if exc.orig else str(exc)
    if "exclude_doctor_appointment_overlap" in error_msg:
        raise DoubleBookingError("Médico já possui um atendimento neste horário")
    if "exclude_patient_appointment_overlap" in error_msg:
        raise DoubleBookingError("Paciente já possui um atendimento neste horário")
    raise exc


class AppointmentService:
    @staticmethod
    def list_appointments() -> list[Appointment]:
        """Retorna todos os atendimentos."""
        return Appointment.query.all()

    @staticmethod
    def get_appointment(appointment_id: int) -> Appointment:
        """Busca um atendimento pelo ID."""
        appointment = db.session.get(Appointment, appointment_id)
        if not appointment:
            raise EntityNotFoundError("Atendimento", appointment_id)

        return appointment

    @staticmethod
    def create_appointment(
        doctor_id: int,
        patient_id: int,
        scheduled_at: datetime,
        notes: str | None = None,
    ) -> Appointment:
        """Cria um novo atendimento."""
        if not db.session.get(Doctor, doctor_id):
            raise EntityNotFoundError("Médico", doctor_id)
        if not db.session.get(Patient, patient_id):
            raise EntityNotFoundError("Paciente", patient_id)

        appointment = Appointment(
            doctor_id=doctor_id,
            patient_id=patient_id,
            scheduled_at=scheduled_at,
            notes=notes,
        )
        db.session.add(appointment)
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            _handle_integrity_error(exc)
        return appointment

    @staticmethod
    def update_appointment(
        appointment_id: int,
        doctor_id: int | None = None,
        patient_id: int | None = None,
        scheduled_at: datetime | None = None,
        status: str | None = None,
        notes: str | None = None,
    ) -> Appointment:
        """Atualiza um atendimento existente."""
        appointment = db.session.get(Appointment, appointment_id)
        if not appointment:
            raise EntityNotFoundError("Atendimento", appointment_id)

        if doctor_id is not None:
            if not db.session.get(Doctor, doctor_id):
                raise EntityNotFoundError("Médico", doctor_id)
            appointment.doctor_id = doctor_id

        if patient_id is not None:
            if not db.session.get(Patient, patient_id):
                raise EntityNotFoundError("Paciente", patient_id)
            appointment.patient_id = patient_id

        if scheduled_at is not None:
            appointment.scheduled_at = scheduled_at

        if status is not None:
            appointment.status = AppointmentStatus(status)

        if notes is not None:
            appointment.notes = notes

        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            _handle_integrity_error(exc)
        return appointment

    @staticmethod
    def delete_appointment(appointment_id: int) -> None:
        """Remove um atendimento."""
        appointment = db.session.get(Appointment, appointment_id)
        if not appointment:
            raise EntityNotFoundError("Atendimento", appointment_id)
        db.session.delete(appointment)
        db.session.commit()
