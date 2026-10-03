"""
tests/test_auth_full.py
Full authentication tests using conftest fixtures.
"""
import pytest
import datetime
import jwt as pyjwt
from tests.conftest import auth_header, JWT_SECRET, _make_rgb_image_bytes


# ─── Registration ────────────────────────────────────────────────────────────

class TestRegistration:
    def test_valid_registration(self, client, clean_db):
        resp = client.post('/api/v1/auth/register', json={
            "name": "Test User",
            "email": "newuser@example.com",
            "password": "StrongPass123!"
        })
        assert resp.status_code == 201
        assert resp.json["success"] is True
        assert "user" in resp.json["data"]
        assert "password_hash" not in str(resp.json)
        assert "password" not in str(resp.json["data"]["user"])

    def test_duplicate_email(self, client, clean_db):
        payload = {"name": "Alice", "email": "dup@test.com", "password": "Password123!"}
        client.post('/api/v1/auth/register', json=payload)
        resp = client.post('/api/v1/auth/register', json=payload)
        assert resp.status_code == 409
        assert resp.json["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    def test_invalid_email(self, client, clean_db):
        resp = client.post('/api/v1/auth/register', json={
            "name": "User", "email": "not-an-email", "password": "Password123!"
        })
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "INVALID_EMAIL"

    def test_weak_password(self, client, clean_db):
        resp = client.post('/api/v1/auth/register', json={
            "name": "User", "email": "x@test.com", "password": "short"
        })
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "WEAK_PASSWORD"

    def test_missing_fields(self, client, clean_db):
        resp = client.post('/api/v1/auth/register', json={"name": "Only Name"})
        assert resp.status_code == 400

    def test_password_not_in_response(self, client, clean_db):
        resp = client.post('/api/v1/auth/register', json={
            "name": "SafeUser", "email": "safe@test.com", "password": "Password123!"
        })
        assert resp.status_code == 201
        body = str(resp.json)
        assert "password_hash" not in body
        assert "Password123" not in body


# ─── Login ───────────────────────────────────────────────────────────────────

class TestLogin:
    def test_valid_login(self, client, clean_db, app):
        with app.app_context():
            from tests.conftest import _insert_user
            from app.extensions import mongo
            _insert_user(mongo.get_db(), "login@test.com")

        resp = client.post('/api/v1/auth/login', json={
            "email": "login@test.com", "password": "Password123!"
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json["data"]
        assert resp.json["data"]["token_type"] == "Bearer"
        assert "password_hash" not in str(resp.json)

    def test_wrong_password(self, client, clean_db, app):
        with app.app_context():
            from tests.conftest import _insert_user
            from app.extensions import mongo
            _insert_user(mongo.get_db(), "login2@test.com")

        resp = client.post('/api/v1/auth/login', json={
            "email": "login2@test.com", "password": "WrongPassword!"
        })
        assert resp.status_code == 401
        assert resp.json["error"]["code"] == "INVALID_CREDENTIALS"

    def test_nonexistent_user(self, client, clean_db):
        resp = client.post('/api/v1/auth/login', json={
            "email": "nobody@nowhere.com", "password": "Password123!"
        })
        assert resp.status_code == 401
        assert resp.json["error"]["code"] == "INVALID_CREDENTIALS"

    def test_inactive_user_login(self, client, inactive_user):
        resp = client.post('/api/v1/auth/login', json={
            "email": "inactive@test.com", "password": "Password123!"
        })
        assert resp.status_code == 403
        assert resp.json["error"]["code"] == "ACCOUNT_INACTIVE"

    def test_missing_credentials(self, client, clean_db):
        resp = client.post('/api/v1/auth/login', json={})
        assert resp.status_code == 401


# ─── /me ─────────────────────────────────────────────────────────────────────

class TestAuthMe:
    def test_me_valid_token(self, client, user_a):
        resp = client.get('/api/v1/auth/me', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        assert resp.json["data"]["user"]["email"] == "user_a@test.com"
        assert "password_hash" not in str(resp.json)

    def test_me_no_token(self, client):
        resp = client.get('/api/v1/auth/me')
        assert resp.status_code == 401
        assert resp.json["error"]["code"] == "MISSING_TOKEN"

    def test_me_invalid_token(self, client):
        resp = client.get('/api/v1/auth/me', headers={"Authorization": "Bearer garbage"})
        assert resp.status_code == 401
        assert resp.json["error"]["code"] == "INVALID_TOKEN"

    def test_me_expired_token(self, client, app):
        now = datetime.datetime.now(datetime.timezone.utc)
        expired = pyjwt.encode(
            {"sub": str("000000000000000000000001"),
             "iat": now - datetime.timedelta(hours=48),
             "exp": now - datetime.timedelta(hours=24)},
            app.config["JWT_SECRET_KEY"], algorithm="HS256"
        )
        resp = client.get('/api/v1/auth/me', headers={"Authorization": f"Bearer {expired}"})
        assert resp.status_code == 401
        assert resp.json["error"]["code"] == "EXPIRED_TOKEN"

    def test_inactive_user_protected_route(self, client, inactive_user):
        resp = client.get('/api/v1/auth/me', headers=auth_header(inactive_user["token"]))
        assert resp.status_code == 403
        assert resp.json["error"]["code"] == "ACCOUNT_INACTIVE"
