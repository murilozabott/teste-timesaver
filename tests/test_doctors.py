from app.ext.database import db
from app.models import Doctor


def _create_doctor(crm="CRM001", name="Dr. House", specialty="Diagnostics"):
    doctor = Doctor(name=name, specialty=specialty, crm=crm)
    db.session.add(doctor)
    db.session.flush()
    return doctor


class TestDoctorList:
    def test_list_empty(self, client):
        """GET /doctors é público"""
        resp = client.get("/api/v1/doctors")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_returns_doctors(self, client):
        _create_doctor(crm="CRM100")
        _create_doctor(crm="CRM200", name="Dr. Wilson", specialty="Oncology")

        resp = client.get("/api/v1/doctors")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2
        crms = {d["crm"] for d in data}
        assert crms == {"CRM100", "CRM200"}

    def test_create_doctor(self, client, admin_headers):
        resp = client.post(
            "/api/v1/doctors",
            json={"name": "Dr. New", "specialty": "Cardiology", "crm": "CRM999"},
            headers=admin_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Dr. New"
        assert data["specialty"] == "Cardiology"
        assert data["crm"] == "CRM999"
        assert "id" in data

    def test_create_doctor_requires_admin(self, client, employee_headers):
        resp = client.post(
            "/api/v1/doctors",
            json={"name": "Dr. New", "specialty": "Cardiology", "crm": "CRM999"},
            headers=employee_headers,
        )
        assert resp.status_code == 403

    def test_create_doctor_unauthenticated(self, client):
        resp = client.post(
            "/api/v1/doctors",
            json={"name": "Dr. New", "specialty": "Cardiology", "crm": "CRM999"},
        )
        assert resp.status_code == 401

    def test_create_doctor_duplicate_crm(self, client, admin_headers):
        _create_doctor(crm="CRM_DUP")

        resp = client.post(
            "/api/v1/doctors",
            json={"name": "Another", "specialty": "General", "crm": "CRM_DUP"},
            headers=admin_headers,
        )
        assert resp.status_code == 409

    def test_create_doctor_missing_fields(self, client, admin_headers):
        resp = client.post(
            "/api/v1/doctors",
            json={"name": "Incomplete"},
            headers=admin_headers,
        )
        assert resp.status_code == 400


class TestDoctorDetail:
    def test_get_by_crm(self, client):
        """GET /doctors/<crm> é público"""
        _create_doctor(crm="CRM_GET", name="Dr. Get", specialty="Neurology")

        resp = client.get("/api/v1/doctors/CRM_GET")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["crm"] == "CRM_GET"
        assert data["name"] == "Dr. Get"

    def test_get_not_found(self, client):
        resp = client.get("/api/v1/doctors/NONEXISTENT")
        assert resp.status_code == 404

    def test_delete(self, client, admin_headers):
        _create_doctor(crm="CRM_DEL")

        resp = client.delete("/api/v1/doctors/CRM_DEL", headers=admin_headers)
        assert resp.status_code == 204

        resp = client.get("/api/v1/doctors/CRM_DEL")
        assert resp.status_code == 404

    def test_delete_requires_admin(self, client, employee_headers):
        _create_doctor(crm="CRM_DEL2")

        resp = client.delete("/api/v1/doctors/CRM_DEL2", headers=employee_headers)
        assert resp.status_code == 403

    def test_delete_not_found(self, client, admin_headers):
        resp = client.delete("/api/v1/doctors/GHOST", headers=admin_headers)
        assert resp.status_code == 404
