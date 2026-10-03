"""
tests/test_clothing_full.py
Full clothing catalog tests using conftest fixtures.
"""
import pytest
from bson.objectid import ObjectId
from tests.conftest import auth_header


def _create_clothing(client, token, **kwargs):
    payload = {
        "name": "Test Shirt",
        "category": "shirt",
        "price": 999.0,
        "color": "blue",
        "sizes": ["S", "M", "L"],
    }
    payload.update(kwargs)
    return client.post('/api/v1/clothing', headers=auth_header(token), json=payload)


class TestClothingCreate:
    def test_admin_can_create(self, client, admin_user):
        resp = _create_clothing(client, admin_user["token"])
        assert resp.status_code == 201
        assert resp.json["data"]["clothing"]["name"] == "Test Shirt"

    def test_user_cannot_create(self, client, user_a):
        resp = _create_clothing(client, user_a["token"])
        assert resp.status_code == 403
        assert resp.json["error"]["code"] == "FORBIDDEN"

    def test_unauthenticated_cannot_create(self, client):
        resp = client.post('/api/v1/clothing', json={"name": "x"})
        assert resp.status_code == 401

    def test_invalid_category(self, client, admin_user):
        resp = _create_clothing(client, admin_user["token"], category="jeans")
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "INVALID_CATEGORY"

    def test_negative_price(self, client, admin_user):
        resp = _create_clothing(client, admin_user["token"], price=-100)
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "INVALID_PRICE"

    def test_invalid_price_string(self, client, admin_user):
        resp = _create_clothing(client, admin_user["token"], price="expensive")
        assert resp.status_code == 400

    def test_missing_required_fields(self, client, admin_user):
        resp = client.post('/api/v1/clothing', headers=auth_header(admin_user["token"]), json={})
        assert resp.status_code == 400

    def test_all_valid_categories(self, client, admin_user):
        valid = ["t-shirt", "shirt", "hoodie", "jacket", "dress", "top"]
        for cat in valid:
            resp = _create_clothing(client, admin_user["token"], name=f"Test {cat}", category=cat)
            assert resp.status_code == 201, f"Failed for category: {cat}"


class TestClothingList:
    def test_list_returns_items(self, client, user_a, admin_user):
        _create_clothing(client, admin_user["token"])
        resp = client.get('/api/v1/clothing', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        assert "items" in resp.json["data"]
        assert "pagination" in resp.json["data"]

    def test_unauthenticated_cannot_list(self, client):
        resp = client.get('/api/v1/clothing')
        assert resp.status_code == 401

    def test_filter_by_category(self, client, user_a, admin_user):
        _create_clothing(client, admin_user["token"], category="hoodie", name="Blue Hoodie")
        _create_clothing(client, admin_user["token"], category="shirt", name="White Shirt")
        resp = client.get('/api/v1/clothing?category=hoodie', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        for item in resp.json["data"]["items"]:
            assert item["category"] == "hoodie"

    def test_pagination(self, client, user_a, admin_user):
        for i in range(3):
            _create_clothing(client, admin_user["token"], name=f"Item {i}")
        resp = client.get('/api/v1/clothing?page=1&limit=2', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        assert len(resp.json["data"]["items"]) <= 2

    def test_search(self, client, user_a, admin_user):
        _create_clothing(client, admin_user["token"], name="UniqueSearchableName")
        resp = client.get('/api/v1/clothing?search=UniqueSearchableName', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        found = any("UniqueSearchableName" in i["name"] for i in resp.json["data"]["items"])
        assert found


class TestClothingGetSingle:
    def test_get_valid_item(self, client, user_a, admin_user):
        cr = _create_clothing(client, admin_user["token"])
        cid = cr.json["data"]["clothing"]["id"]
        resp = client.get(f'/api/v1/clothing/{cid}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200

    def test_get_invalid_id(self, client, user_a):
        resp = client.get('/api/v1/clothing/not-an-id', headers=auth_header(user_a["token"]))
        assert resp.status_code == 400

    def test_get_nonexistent(self, client, user_a):
        fake_id = str(ObjectId())
        resp = client.get(f'/api/v1/clothing/{fake_id}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 404


class TestClothingUpdate:
    def test_admin_can_update(self, client, admin_user):
        cr = _create_clothing(client, admin_user["token"])
        cid = cr.json["data"]["clothing"]["id"]
        resp = client.put(
            f'/api/v1/clothing/{cid}',
            headers=auth_header(admin_user["token"]),
            json={"name": "Updated Name"}
        )
        assert resp.status_code == 200
        assert resp.json["data"]["clothing"]["name"] == "Updated Name"

    def test_user_cannot_update(self, client, user_a, admin_user):
        cr = _create_clothing(client, admin_user["token"])
        cid = cr.json["data"]["clothing"]["id"]
        resp = client.put(
            f'/api/v1/clothing/{cid}',
            headers=auth_header(user_a["token"]),
            json={"name": "Hacked"}
        )
        assert resp.status_code == 403


class TestClothingDelete:
    def test_admin_can_deactivate(self, client, admin_user, user_a):
        cr = _create_clothing(client, admin_user["token"])
        cid = cr.json["data"]["clothing"]["id"]
        resp = client.delete(f'/api/v1/clothing/{cid}', headers=auth_header(admin_user["token"]))
        assert resp.status_code == 200

        # After deactivation, item should still exist (soft delete)
        resp2 = client.get(f'/api/v1/clothing/{cid}', headers=auth_header(user_a["token"]))
        assert resp2.status_code == 200  # Item still exists (soft delete)
        assert resp2.json["data"]["clothing"]["available"] is False

    def test_user_cannot_delete(self, client, user_a, admin_user):
        cr = _create_clothing(client, admin_user["token"])
        cid = cr.json["data"]["clothing"]["id"]
        resp = client.delete(f'/api/v1/clothing/{cid}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 403
