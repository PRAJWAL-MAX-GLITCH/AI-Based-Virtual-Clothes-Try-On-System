"""
tests/test_security_full.py
Comprehensive security tests using conftest fixtures.
"""
import pytest
import datetime
import jwt as pyjwt
from bson.objectid import ObjectId
from tests.conftest import auth_header


class TestJWTProtection:
    def test_no_token_returns_401(self, client):
        resp = client.get('/api/v1/users/me')
        assert resp.status_code == 401
        assert resp.json["error"]["code"] == "MISSING_TOKEN"

    def test_malformed_token_returns_401(self, client):
        resp = client.get('/api/v1/users/me', headers={"Authorization": "Bearer !!!!"})
        assert resp.status_code == 401
        assert resp.json["error"]["code"] == "INVALID_TOKEN"

    def test_wrong_signature_returns_401(self, client):
        fake = pyjwt.encode({"sub": "123"}, "wrong-secret", algorithm="HS256")
        resp = client.get('/api/v1/users/me', headers={"Authorization": f"Bearer {fake}"})
        assert resp.status_code == 401
        assert resp.json["error"]["code"] == "INVALID_TOKEN"

    def test_expired_token_returns_401(self, client, app):
        now = datetime.datetime.now(datetime.timezone.utc)
        expired = pyjwt.encode(
            {"sub": str(ObjectId()), "iat": now - datetime.timedelta(hours=25),
             "exp": now - datetime.timedelta(hours=1)},
            app.config["JWT_SECRET_KEY"], algorithm="HS256"
        )
        resp = client.get('/api/v1/users/me', headers={"Authorization": f"Bearer {expired}"})
        assert resp.status_code == 401
        assert resp.json["error"]["code"] == "EXPIRED_TOKEN"

    def test_inactive_user_rejected(self, client, inactive_user):
        resp = client.get('/api/v1/users/me', headers=auth_header(inactive_user["token"]))
        assert resp.status_code == 403
        assert resp.json["error"]["code"] == "ACCOUNT_INACTIVE"


class TestAdminProtection:
    def test_user_cannot_create_clothing(self, client, user_a):
        resp = client.post(
            '/api/v1/clothing',
            headers=auth_header(user_a["token"]),
            json={"name": "Hack", "category": "shirt", "price": 1.0, "color": "red", "sizes": ["M"]}
        )
        assert resp.status_code == 403
        assert resp.json["error"]["code"] == "FORBIDDEN"

    def test_user_cannot_update_clothing(self, client, user_a, admin_user):
        cr = client.post(
            '/api/v1/clothing',
            headers=auth_header(admin_user["token"]),
            json={"name": "Legit Shirt", "category": "shirt", "price": 500, "color": "blue", "sizes": ["M"]}
        )
        cid = cr.json["data"]["clothing"]["id"]
        resp = client.put(
            f'/api/v1/clothing/{cid}',
            headers=auth_header(user_a["token"]),
            json={"name": "Hacked"}
        )
        assert resp.status_code == 403

    def test_user_cannot_delete_clothing(self, client, user_a, admin_user):
        cr = client.post(
            '/api/v1/clothing',
            headers=auth_header(admin_user["token"]),
            json={"name": "Shirt", "category": "shirt", "price": 500, "color": "blue", "sizes": ["M"]}
        )
        cid = cr.json["data"]["clothing"]["id"]
        resp = client.delete(f'/api/v1/clothing/{cid}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 403


class TestIDORProtection:
    def test_user_a_cannot_access_user_b_history(self, client, user_a, user_b, app):
        with app.app_context():
            from app.extensions import mongo
            from bson.objectid import ObjectId
            import datetime
            db = mongo.get_db()
            hid = db.tryon_history.insert_one({
                "user_id": ObjectId(user_b["id"]),
                "result_image": "results/private.png",
                "created_at": datetime.datetime.now(datetime.timezone.utc)
            }).inserted_id

        resp = client.get(f'/api/v1/history/{hid}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 404

    def test_user_a_cannot_delete_user_b_history(self, client, user_a, user_b, app):
        with app.app_context():
            from app.extensions import mongo
            import datetime
            db = mongo.get_db()
            hid = db.tryon_history.insert_one({
                "user_id": ObjectId(user_b["id"]),
                "result_image": "results/private2.png",
                "created_at": datetime.datetime.now(datetime.timezone.utc)
            }).inserted_id

        resp = client.delete(f'/api/v1/history/{hid}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 404

    def test_user_a_cannot_access_user_b_custom_clothing(self, client, user_a, user_b, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            cid = db.user_clothing.insert_one({
                "user_id": ObjectId(user_b["id"]),
                "name": "B Shirt",
                "category": "shirt",
                "image": "clothing/user/bshirt.png",
                "available": True,
            }).inserted_id

        resp = client.get(f'/api/v1/user-clothing/{cid}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 404

    def test_user_a_cannot_delete_user_b_custom_clothing(self, client, user_a, user_b, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            cid = db.user_clothing.insert_one({
                "user_id": ObjectId(user_b["id"]),
                "name": "B Shirt",
                "category": "shirt",
                "image": "clothing/user/bshirt2.png",
                "available": True,
            }).inserted_id

        resp = client.delete(f'/api/v1/user-clothing/{cid}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 404


class TestPathTraversal:
    def test_static_path_traversal_blocked(self, client, user_a):
        resp = client.get(
            '/api/v1/static/../../etc/passwd',
            headers=auth_header(user_a["token"])
        )
        assert resp.status_code == 403

    def test_static_unauthenticated(self, client):
        resp = client.get('/api/v1/static/results/some.png')
        assert resp.status_code == 401


class TestRoleEscalation:
    def test_role_field_in_update_ignored(self, client, user_a):
        resp = client.put(
            '/api/v1/users/me',
            headers=auth_header(user_a["token"]),
            json={"name": "Test", "role": "admin"}
        )
        assert resp.status_code == 200
        assert resp.json["data"]["user"]["role"] == "user"

    def test_is_active_field_in_update_ignored(self, client, user_a):
        resp = client.put(
            '/api/v1/users/me',
            headers=auth_header(user_a["token"]),
            json={"name": "Test", "is_active": False}
        )
        assert resp.status_code == 200
        assert resp.json["data"]["user"]["is_active"] is True


class TestErrorHandlers:
    def test_404_returns_json(self, client):
        resp = client.get('/api/v1/does-not-exist-endpoint-xyz')
        assert resp.status_code == 404
        assert resp.content_type == "application/json"
        assert resp.json["error"]["code"] == "NOT_FOUND"
        assert "success" in resp.json
        assert resp.json["success"] is False

    def test_no_stack_trace_in_404(self, client):
        resp = client.get('/api/v1/this-is-not-real')
        body = str(resp.json)
        assert "Traceback" not in body
        assert "File \"" not in body

    def test_405_returns_json(self, client):
        resp = client.get('/api/v1/auth/register')  # Only POST allowed
        assert resp.status_code == 405
        assert resp.content_type == "application/json"

    def test_password_not_in_any_response(self, client, user_a):
        resp = client.get('/api/v1/users/me', headers=auth_header(user_a["token"]))
        assert "password_hash" not in str(resp.json)
        assert "password" not in str(resp.json["data"])
