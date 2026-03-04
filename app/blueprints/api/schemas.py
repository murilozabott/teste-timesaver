from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr


class DoctorCreate(BaseModel):
    """
    Schema para validar payload da requisição de inserção de médico
    """

    name: str
    specialty: str
    crm: str


class PatientCreate(BaseModel):
    """
    Schema para validar payload da requisição de inserção de paciente
    """

    name: str
    email: EmailStr
    birth_date: date


class AppointmentCreate(BaseModel):
    """
    Schema para validar payload da requisição de criação de consulta
    """

    doctor_id: int
    patient_id: int
    scheduled_at: datetime
    notes: str | None = None


class AppointmentUpdate(BaseModel):
    """
    Schema para validar payload da requisição de atualização de consulta
    """

    doctor_id: int | None = None
    patient_id: int | None = None
    scheduled_at: datetime | None = None
    status: Literal["scheduled", "canceled", "completed"] | None = None
    notes: str | None = None
