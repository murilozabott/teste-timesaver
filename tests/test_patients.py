from datetime import date

from app.ext.database import db
from app.models import Patient


def _create_patient(
    name="John Doe",
    email="john@example.com",
    birth_date=None,
):
    patient = Patient(
        name=name,
        email=email,
        birth_date=birth_date or date(1990, 1, 15),
    )
    db.session.add(patient)
    db.session.flush()
    return patient


class TestPatientList:
    def test_list_empty(self, client, admin_headers):
        resp = client.get("/api/v1/patients", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_requires_admin(self, client, employee_headers):
        resp = client.get("/api/v1/patients", headers=employee_headers)
        assert resp.status_code == 403

    def test_list_unauthenticated(self, client):
        resp = client.get("/api/v1/patients")
        assert resp.status_code == 401

    def test_list_returns_patients(self, client, admin_headers):
        _create_patient(name="Alice", email="alice@example.com")
        _create_patient(name="Bob", email="bob@example.com")

        resp = client.get("/api/v1/patients", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2
        names = {p["name"] for p in data}
        assert names == {"Alice", "Bob"}

    def test_create_patient(self, client, admin_headers):
        resp = client.post(
            "/api/v1/patients",
            json={
                "name": "Jane Doe",
                "email": "jane@example.com",
                "birth_date": "1985-06-20",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Jane Doe"
        assert data["email"] == "jane@example.com"
        assert data["birth_date"] == "1985-06-20"
        assert "id" in data

    def test_create_patient_invalid_email(self, client, admin_headers):
        resp = client.post(
            "/api/v1/patients",
            json={
                "name": "Bad Email",
                "email": "not-an-email",
                "birth_date": "2000-01-01",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 400

    def test_create_patient_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/v1/patients",
            json={"name": "Only Name"},
            headers=admin_headers,
        )
        assert resp.status_code == 400


class TestPatientDetail:
    def test_get_by_id(self, client, admin_headers):
        patient = _create_patient(name="Lookup Patient")

        resp = client.get(f"/api/v1/patients/{patient.id}", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Lookup Patient"
        assert data["id"] == patient.id

    def test_get_not_found(self, client, admin_headers):
        resp = client.get("/api/v1/patients/999999", headers=admin_headers)
        assert resp.status_code == 404

    def test_delete(self, client, admin_headers):
        patient = _create_patient(name="To Delete")

        resp = client.delete(f"/api/v1/patients/{patient.id}", headers=admin_headers)
        assert resp.status_code == 204

        resp = client.get(f"/api/v1/patients/{patient.id}", headers=admin_headers)
        assert resp.status_code == 404

    def test_delete_not_found(self, client, admin_headers):
        resp = client.delete("/api/v1/patients/999999", headers=admin_headers)
        assert resp.status_code == 404
