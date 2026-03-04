from app.ext.database import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)

    appointments = db.relationship("Appointment", back_populates="patient")
