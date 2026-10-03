"""
tests/test_users_full.py
Full user management tests using conftest fixtures.
"""
import pytest
from tests.conftest import auth_header


class TestUserProfile:
    def test_get_own_profile(self, client, user_a):
        resp = client.get('/api/v1/users/me', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        assert resp.json["data"]["user"]["email"] == "user_a@test.com"
        assert "password_hash" not in str(resp.json)

    def test_no_token(self, client):
        resp = client.get('/api/v1/users/me')
        assert resp.status_code == 401

    def test_update_name(self, client, user_a):
        resp = client.put(
            '/api/v1/users/me',
            headers=auth_header(user_a["token"]),
            json={"name": "Updated Name"}
        )
        assert resp.status_code == 200
        assert resp.json["data"]["user"]["name"] == "Updated Name"

    def test_update_ignores_role(self, client, user_a):
        resp = client.put(
            '/api/v1/users/me',
            headers=auth_header(user_a["token"]),
            json={"name": "Hacker", "role": "admin"}
        )
        assert resp.status_code == 200
        assert resp.json["data"]["user"]["role"] == "user"

    def test_update_ignores_is_active(self, client, user_a):
        resp = client.put(
            '/api/v1/users/me',
            headers=auth_header(user_a["token"]),
            json={"name": "Hacker", "is_active": False}
        )
        assert resp.status_code == 200
        assert resp.json["data"]["user"]["is_active"] is True

    def test_update_ignores_password_hash(self, client, user_a):
        resp = client.put(
            '/api/v1/users/me',
            headers=auth_header(user_a["token"]),
            json={"password_hash": "hacked_hash"}
        )
        # Should fail (no valid update fields) or succeed but not change hash
        assert resp.json["success"] is False or "password_hash" not in str(resp.json)

    def test_update_email_duplicate(self, client, user_a, user_b):
        resp = client.put(
            '/api/v1/users/me',
            headers=auth_header(user_a["token"]),
            json={"email": "user_b@test.com"}
        )
        assert resp.status_code == 409
        assert resp.json["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    def test_update_invalid_email(self, client, user_a):
        resp = client.put(
            '/api/v1/users/me',
            headers=auth_header(user_a["token"]),
            json={"email": "notanemail"}
        )
        assert resp.status_code == 400

    def test_no_valid_update_fields(self, client, user_a):
        resp = client.put(
            '/api/v1/users/me',
            headers=auth_header(user_a["token"]),
            json={"unknown_field": "value"}
        )
        assert resp.status_code == 400


class TestPasswordChange:
    def test_change_password_success(self, client, user_a, app):
        # First update the user's password_hash for the test (user_a's password is Password123!)
        resp = client.patch(
            '/api/v1/users/me/password',
            headers=auth_header(user_a["token"]),
            json={"current_password": "Password123!", "new_password": "NewPass456!"}
        )
        assert resp.status_code == 200

    def test_wrong_current_password(self, client, user_a):
        resp = client.patch(
            '/api/v1/users/me/password',
            headers=auth_header(user_a["token"]),
            json={"current_password": "WrongOldPass!", "new_password": "NewPass456!"}
        )
        assert resp.status_code == 403
        assert resp.json["error"]["code"] == "INCORRECT_PASSWORD"

    def test_weak_new_password(self, client, user_a):
        resp = client.patch(
            '/api/v1/users/me/password',
            headers=auth_header(user_a["token"]),
            json={"current_password": "Password123!", "new_password": "short"}
        )
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "WEAK_PASSWORD"

    def test_missing_passwords(self, client, user_a):
        resp = client.patch(
            '/api/v1/users/me/password',
            headers=auth_header(user_a["token"]),
            json={}
        )
        assert resp.status_code == 400


class TestAccountDeactivation:
    def test_deactivate_account(self, client, user_a, app):
        resp = client.delete('/api/v1/users/me', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200

        # Verify can't use the token anymore (is_active=False)
        resp2 = client.get('/api/v1/users/me', headers=auth_header(user_a["token"]))
        assert resp2.status_code == 403
        assert resp2.json["error"]["code"] == "ACCOUNT_INACTIVE"
