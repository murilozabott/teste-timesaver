import enum

from app.ext.database import db


class AppointmentStatus(enum.Enum):
    SCHEDULED = "scheduled"
    CANCELED = "canceled"
    COMPLETED = "completed"


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(
        db.Enum(AppointmentStatus),
        default=AppointmentStatus.SCHEDULED,
        nullable=False,
    )
    notes = db.Column(db.Text)

    doctor = db.relationship("Doctor", back_populates="appointments")
    patient = db.relationship("Patient", back_populates="appointments")
