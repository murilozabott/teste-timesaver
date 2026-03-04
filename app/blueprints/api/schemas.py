from datetime import date

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
