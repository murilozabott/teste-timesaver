from datetime import date, datetime

from app.ext.database import db
from app.models import Doctor, Patient
from app.models.appointment import Appointment


def _create_doctor(crm="CRM001", name="Dr. House", specialty="Diagnostics"):
    doctor = Doctor(name=name, specialty=specialty, crm=crm)
    db.session.add(doctor)
    db.session.flush()
    return doctor


def _create_patient(name="John Doe", email="john@example.com", birth_date=None):
    patient = Patient(
        name=name,
        email=email,
        birth_date=birth_date or date(1990, 1, 15),
    )
    db.session.add(patient)
    db.session.flush()
    return patient


def _create_appointment(doctor=None, patient=None, scheduled_at=None, notes=None):
    doctor = doctor or _create_doctor()
    patient = patient or _create_patient()
    scheduled_at = scheduled_at or datetime(2026, 6, 15, 10, 0)

    appointment = Appointment(
        doctor_id=doctor.id,
        patient_id=patient.id,
        scheduled_at=scheduled_at,
        notes=notes,
    )
    db.session.add(appointment)
    db.session.flush()
    return appointment


class TestAppointmentList:
    def test_list_empty(self, client):
        resp = client.get("/api/v1/appointments")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_returns_appointments(self, client):
        doctor = _create_doctor(crm="CRM_LIST")
        patient = _create_patient(name="Patient List", email="list@example.com")
        _create_appointment(
            doctor=doctor,
            patient=patient,
            scheduled_at=datetime(2026, 7, 1, 9, 0),
        )

        resp = client.get("/api/v1/appointments")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["doctor_id"] == doctor.id
        assert data[0]["patient_id"] == patient.id

    def test_create_appointment(self, client):
        doctor = _create_doctor(crm="CRM_CREATE")
        patient = _create_patient(name="Patient Create", email="create@example.com")

        resp = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": patient.id,
                "scheduled_at": "2026-08-01T14:00:00",
                "notes": "Routine checkup",
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["doctor_id"] == doctor.id
        assert data["patient_id"] == patient.id
        assert data["status"] == "scheduled"
        assert data["notes"] == "Routine checkup"
        assert "id" in data

    def test_create_appointment_missing_fields(self, client):
        resp = client.post(
            "/api/v1/appointments",
            json={"doctor_id": 1},
        )
        assert resp.status_code == 400

    def test_create_appointment_doctor_not_found(self, client):
        patient = _create_patient(name="Orphan", email="orphan@example.com")

        resp = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": 999999,
                "patient_id": patient.id,
                "scheduled_at": "2026-08-01T14:00:00",
            },
        )
        assert resp.status_code == 404

    def test_create_appointment_patient_not_found(self, client):
        doctor = _create_doctor(crm="CRM_ORPHAN")

        resp = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": 999999,
                "scheduled_at": "2026-08-01T14:00:00",
            },
        )
        assert resp.status_code == 404


class TestAppointmentDetail:
    def test_get_by_id(self, client):
        appt = _create_appointment(notes="Test note")

        resp = client.get(f"/api/v1/appointments/{appt.id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["id"] == appt.id
        assert data["notes"] == "Test note"
        assert data["status"] == "scheduled"

    def test_get_not_found(self, client):
        resp = client.get("/api/v1/appointments/999999")
        assert resp.status_code == 404

    def test_update_status(self, client):
        appt = _create_appointment()

        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json={"status": "completed"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "completed"

    def test_update_notes(self, client):
        appt = _create_appointment()

        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json={"notes": "Updated notes"},
        )
        assert resp.status_code == 200
        assert resp.get_json()["notes"] == "Updated notes"

    def test_update_scheduled_at(self, client):
        appt = _create_appointment()

        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json={"scheduled_at": "2026-12-25T10:00:00"},
        )
        assert resp.status_code == 200
        assert "2026-12-25" in resp.get_json()["scheduled_at"]

    def test_update_not_found(self, client):
        resp = client.put(
            "/api/v1/appointments/999999",
            json={"status": "canceled"},
        )
        assert resp.status_code == 404

    def test_update_doctor(self, client):
        appt = _create_appointment()
        new_doctor = _create_doctor(crm="CRM_NEW_DOC")

        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json={"doctor_id": new_doctor.id},
        )
        assert resp.status_code == 200
        assert resp.get_json()["doctor_id"] == new_doctor.id

    def test_update_patient(self, client):
        appt = _create_appointment()
        new_patient = _create_patient(
            name="New Patient", email="newpatient@example.com"
        )

        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json={"patient_id": new_patient.id},
        )
        assert resp.status_code == 200
        assert resp.get_json()["patient_id"] == new_patient.id

    def test_update_nonexistent_doctor(self, client):
        appt = _create_appointment()

        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json={"doctor_id": 999999},
        )
        assert resp.status_code == 404

    def test_update_nonexistent_patient(self, client):
        appt = _create_appointment()

        resp = client.put(
            f"/api/v1/appointments/{appt.id}",
            json={"patient_id": 999999},
        )
        assert resp.status_code == 404

    def test_delete(self, client):
        appt = _create_appointment()

        resp = client.delete(f"/api/v1/appointments/{appt.id}")
        assert resp.status_code == 204

        resp = client.get(f"/api/v1/appointments/{appt.id}")
        assert resp.status_code == 404

    def test_delete_not_found(self, client):
        resp = client.delete("/api/v1/appointments/999999")
        assert resp.status_code == 404


class TestDoubleBooking:
    """Testes para a restrição EXCLUDE que impede agendamentos sobrepostos
    (dentro de 5 minutos) para o mesmo médico ou paciente."""

    def test_doctor_double_booking_same_time(self, client):
        """Mesmo médico, pacients diferentes, EXATO mesmo horário -> 409."""
        doctor = _create_doctor(crm="CRM_DBL_DOC")
        p1 = _create_patient(name="Patient A", email="a@example.com")
        p2 = _create_patient(name="Patient B", email="b@example.com")
        scheduled = "2026-09-01T10:00:00"

        resp1 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": p1.id,
                "scheduled_at": scheduled,
            },
        )
        assert resp1.status_code == 201

        resp2 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": p2.id,
                "scheduled_at": scheduled,
            },
        )
        assert resp2.status_code == 409

    def test_doctor_double_booking_within_5_minutes(self, client):
        """Mesmo médico, pacientes diferentes, 3 minutos de diferença -> 409."""
        doctor = _create_doctor(crm="CRM_DBL_DOC2")
        p1 = _create_patient(name="Patient C", email="c@example.com")
        p2 = _create_patient(name="Patient D", email="d@example.com")

        resp1 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": p1.id,
                "scheduled_at": "2026-09-02T10:00:00",
            },
        )
        assert resp1.status_code == 201

        resp2 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": p2.id,
                "scheduled_at": "2026-09-02T10:03:00",
            },
        )
        assert resp2.status_code == 409

    def test_doctor_booking_outside_5_minutes(self, client):
        """Mesmo médico, 6 minutos de diferença -> permitido."""
        doctor = _create_doctor(crm="CRM_OK_DOC")
        p1 = _create_patient(name="Patient E", email="e@example.com")
        p2 = _create_patient(name="Patient F", email="f@example.com")

        resp1 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": p1.id,
                "scheduled_at": "2026-09-03T10:00:00",
            },
        )
        assert resp1.status_code == 201

        resp2 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": p2.id,
                "scheduled_at": "2026-09-03T10:06:00",
            },
        )
        assert resp2.status_code == 201

    def test_patient_double_booking_same_time(self, client):
        """Mesmo paciente, mesmo horário com médicos diferentes -> 409."""
        d1 = _create_doctor(crm="CRM_PAT_DBL1")
        d2 = _create_doctor(crm="CRM_PAT_DBL2")
        patient = _create_patient(name="Patient G", email="g@example.com")
        scheduled = "2026-09-04T10:00:00"

        resp1 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": d1.id,
                "patient_id": patient.id,
                "scheduled_at": scheduled,
            },
        )
        assert resp1.status_code == 201

        resp2 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": d2.id,
                "patient_id": patient.id,
                "scheduled_at": scheduled,
            },
        )
        assert resp2.status_code == 409

    def test_patient_double_booking_within_5_minutes(self, client):
        """Mesmo paciente, 2 minutos de diferença com médicos diferentes -> 409."""
        d1 = _create_doctor(crm="CRM_PAT_DBL3")
        d2 = _create_doctor(crm="CRM_PAT_DBL4")
        patient = _create_patient(name="Patient H", email="h@example.com")

        resp1 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": d1.id,
                "patient_id": patient.id,
                "scheduled_at": "2026-09-05T10:00:00",
            },
        )
        assert resp1.status_code == 201

        resp2 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": d2.id,
                "patient_id": patient.id,
                "scheduled_at": "2026-09-05T10:02:00",
            },
        )
        assert resp2.status_code == 409

    def test_patient_booking_outside_5_minutes(self, client):
        """Mesmo paciente, 6 minutos de diferença -> permitido."""
        d1 = _create_doctor(crm="CRM_PAT_OK1")
        d2 = _create_doctor(crm="CRM_PAT_OK2")
        patient = _create_patient(name="Patient I", email="i@example.com")

        resp1 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": d1.id,
                "patient_id": patient.id,
                "scheduled_at": "2026-09-06T10:00:00",
            },
        )
        assert resp1.status_code == 201

        resp2 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": d2.id,
                "patient_id": patient.id,
                "scheduled_at": "2026-09-06T10:06:00",
            },
        )
        assert resp2.status_code == 201

    def test_canceled_appointment_allows_rebooking(self, client):
        """Um agendamento cancelado não deve bloquear um novo no mesmo horário."""
        doctor = _create_doctor(crm="CRM_CANCEL")
        p1 = _create_patient(name="Patient J", email="j@example.com")
        p2 = _create_patient(name="Patient K", email="k@example.com")
        scheduled = "2026-09-07T10:00:00"

        resp1 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": p1.id,
                "scheduled_at": scheduled,
            },
        )
        assert resp1.status_code == 201
        appt_id = resp1.get_json()["id"]

        # Troca o primeiro agendamento p/ cancelado
        resp_cancel = client.put(
            f"/api/v1/appointments/{appt_id}",
            json={"status": "canceled"},
        )
        assert resp_cancel.status_code == 200

        # Novo agendamento ao mesmo tempo do cancelado
        resp2 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": p2.id,
                "scheduled_at": scheduled,
            },
        )
        assert resp2.status_code == 201

    def test_different_doctors_same_time_allowed(self, client):
        """Médicos diferentes no mesmo horário com pacientes diferentes -> permitido."""
        d1 = _create_doctor(crm="CRM_DIFF1")
        d2 = _create_doctor(crm="CRM_DIFF2")
        p1 = _create_patient(name="Patient L", email="l@example.com")
        p2 = _create_patient(name="Patient M", email="m@example.com")
        scheduled = "2026-09-08T10:00:00"

        resp1 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": d1.id,
                "patient_id": p1.id,
                "scheduled_at": scheduled,
            },
        )
        assert resp1.status_code == 201

        resp2 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": d2.id,
                "patient_id": p2.id,
                "scheduled_at": scheduled,
            },
        )
        assert resp2.status_code == 201

    def test_update_causes_doctor_double_booking(self, client):
        """Atualizando o horário de um agendamento para conflitar com outro -> 409."""
        doctor = _create_doctor(crm="CRM_UPD_DBL")
        p1 = _create_patient(name="Patient N", email="n@example.com")
        p2 = _create_patient(name="Patient O", email="o@example.com")

        # Cria 2 agendamentos válidos
        resp1 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": p1.id,
                "scheduled_at": "2026-09-09T10:00:00",
            },
        )
        assert resp1.status_code == 201

        resp2 = client.post(
            "/api/v1/appointments",
            json={
                "doctor_id": doctor.id,
                "patient_id": p2.id,
                "scheduled_at": "2026-09-09T11:00:00",
            },
        )
        assert resp2.status_code == 201
        appt2_id = resp2.get_json()["id"]

        # Troca o segundo agendamento para conflitar com o primeiro
        resp_update = client.put(
            f"/api/v1/appointments/{appt2_id}",
            json={"scheduled_at": "2026-09-09T10:00:00"},
        )
        assert resp_update.status_code == 409
