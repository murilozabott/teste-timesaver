class TestRegister:
    def test_register_employee(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "emp1", "password": "secret123"},
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["username"] == "emp1"
        assert data["role"] == "employee"
        assert "id" in data

    def test_register_admin(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "adm1", "password": "secret123", "role": "admin"},
        )
        assert resp.status_code == 201
        assert resp.get_json()["role"] == "admin"

    def test_register_duplicate_username(self, client):
        client.post(
            "/api/v1/auth/register",
            json={"username": "dup_user", "password": "secret123"},
        )
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "dup_user", "password": "other"},
        )
        assert resp.status_code == 409

    def test_register_missing_fields(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "nopass"},
        )
        assert resp.status_code == 400

    def test_register_invalid_role(self, client):
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": "bad_role", "password": "secret123", "role": "superadmin"},
        )
        assert resp.status_code == 400


class TestLogin:
    def test_login_success(self, client):
        client.post(
            "/api/v1/auth/register",
            json={"username": "login_user", "password": "secret123"},
        )
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "login_user", "password": "secret123"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "access_token" in data

    def test_login_wrong_password(self, client):
        client.post(
            "/api/v1/auth/register",
            json={"username": "wrong_pw", "password": "secret123"},
        )
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "wrong_pw", "password": "wrongpass"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "ghost", "password": "secret123"},
        )
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "nopass"},
        )
        assert resp.status_code == 400


class TestTokenValidation:
    def test_invalid_token(self, client):
        resp = client.get(
            "/api/v1/appointments",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401

    def test_missing_auth_header(self, client):
        resp = client.post(
            "/api/v1/doctors",
            json={"name": "Dr. X", "specialty": "Y", "crm": "Z"},
        )
        assert resp.status_code == 401

    def test_malformed_auth_header(self, client):
        resp = client.get(
            "/api/v1/appointments",
            headers={"Authorization": "NotBearer token"},
        )
        assert resp.status_code == 401


class TestRoleHierarchy:
    def test_admin_can_access_employee_endpoints(self, client, admin_headers):
        """Admin tem acesso a endpoints de employee."""
        resp = client.get("/api/v1/appointments", headers=admin_headers)
        assert resp.status_code == 200

    def test_employee_cannot_access_admin_endpoints(self, client, employee_headers):
        """Employee não pode acessar endpoints de admin."""
        resp = client.post(
            "/api/v1/doctors",
            json={"name": "Dr. X", "specialty": "Y", "crm": "Z"},
            headers=employee_headers,
        )
        assert resp.status_code == 403

    def test_admin_can_access_admin_endpoints(self, client, admin_headers):
        """Admin pode criar médico."""
        resp = client.post(
            "/api/v1/doctors",
            json={"name": "Dr. Admin", "specialty": "Surgery", "crm": "CRM_ADM"},
            headers=admin_headers,
        )
        assert resp.status_code == 201
