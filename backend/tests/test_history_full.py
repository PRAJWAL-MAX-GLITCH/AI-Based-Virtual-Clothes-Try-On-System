"""
tests/test_history_full.py
Full history & result management tests using conftest fixtures.
"""
import os
import datetime
import pytest
from bson.objectid import ObjectId
from tests.conftest import auth_header, _insert_user


def _seed_history(db, user_id, result_image="results/mock_result.png",
                  clothing_source="catalog", clothing_name="Black Shirt",
                  clothing_category="shirt", minutes_ago=0):
    now = datetime.datetime.now(datetime.timezone.utc)
    return db.tryon_history.insert_one({
        "user_id": user_id,
        "result_image": result_image,
        "clothing_category": clothing_category,
        "clothing_source": clothing_source,
        "clothing_name": clothing_name,
        "status": "completed",
        "created_at": now - datetime.timedelta(minutes=minutes_ago),
    }).inserted_id


class TestHistoryList:
    def test_list_history_own_only(self, client, user_a, user_b, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            h_a = _seed_history(db, ObjectId(user_a["id"]))
            h_b = _seed_history(db, ObjectId(user_b["id"]))

        resp = client.get('/api/v1/history', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        ids = [i["id"] for i in resp.json["data"]["items"]]
        assert str(h_a) in ids
        assert str(h_b) not in ids

    def test_list_newest_first(self, client, user_a, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            old_id = _seed_history(db, ObjectId(user_a["id"]), minutes_ago=10)
            new_id = _seed_history(db, ObjectId(user_a["id"]), minutes_ago=2)

        resp = client.get('/api/v1/history', headers=auth_header(user_a["token"]))
        ids = [i["id"] for i in resp.json["data"]["items"]]
        assert ids[0] == str(new_id)
        assert ids[1] == str(old_id)

    def test_pagination(self, client, user_a, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            for i in range(5):
                _seed_history(db, ObjectId(user_a["id"]), minutes_ago=i)

        resp = client.get('/api/v1/history?page=1&limit=2', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        data = resp.json["data"]
        assert len(data["items"]) == 2
        assert data["pagination"]["total"] == 5
        assert data["pagination"]["pages"] == 3

    def test_unauthenticated(self, client):
        resp = client.get('/api/v1/history')
        assert resp.status_code == 401


class TestHistoryGetSingle:
    def test_get_own_history(self, client, user_a, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            hid = _seed_history(db, ObjectId(user_a["id"]), clothing_name="My Shirt")

        resp = client.get(f'/api/v1/history/{hid}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        assert resp.json["data"]["clothing_name"] == "My Shirt"

    def test_cannot_get_other_users_history(self, client, user_a, user_b, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            hid_b = _seed_history(db, ObjectId(user_b["id"]))

        resp = client.get(f'/api/v1/history/{hid_b}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 404  # Hide existence

    def test_invalid_id(self, client, user_a):
        resp = client.get('/api/v1/history/not-a-valid-id', headers=auth_header(user_a["token"]))
        assert resp.status_code in (400, 404)

    def test_nonexistent_id(self, client, user_a):
        fake = str(ObjectId())
        resp = client.get(f'/api/v1/history/{fake}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 404


class TestHistoryDelete:
    def test_delete_own_history_removes_result(self, client, user_a, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            upload_root = app.config["UPLOAD_FOLDER"]
            results_dir = os.path.join(upload_root, "results")
            os.makedirs(results_dir, exist_ok=True)
            img_path = os.path.join(results_dir, "del_test.png")
            with open(img_path, "w") as f:
                f.write("fake")

            hid = _seed_history(db, ObjectId(user_a["id"]), result_image="results/del_test.png")

        resp = client.delete(f'/api/v1/history/{hid}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        assert not os.path.exists(img_path)

    def test_delete_does_not_affect_other_user(self, client, user_a, user_b, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            hid_b = _seed_history(db, ObjectId(user_b["id"]))

        resp = client.delete(f'/api/v1/history/{hid_b}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 404

        # B's record still exists
        resp2 = client.get(f'/api/v1/history/{hid_b}', headers=auth_header(user_b["token"]))
        assert resp2.status_code == 200

    def test_delete_history_not_original_images(self, client, user_a, app):
        """Deleting history should never delete person or clothing images."""
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            upload_root = app.config["UPLOAD_FOLDER"]

            # Create fake person image and clothing image
            person_dir = os.path.join(upload_root, "users")
            clothing_dir = os.path.join(upload_root, "clothing", "catalog")
            os.makedirs(person_dir, exist_ok=True)
            os.makedirs(clothing_dir, exist_ok=True)

            person_path = os.path.join(person_dir, "person_keep.png")
            clothing_path = os.path.join(clothing_dir, "clothing_keep.png")
            result_path_rel = "results/result_to_delete.png"
            result_path_abs = os.path.join(upload_root, result_path_rel)
            os.makedirs(os.path.dirname(result_path_abs), exist_ok=True)

            with open(person_path, "w") as f:
                f.write("person")
            with open(clothing_path, "w") as f:
                f.write("clothing")
            with open(result_path_abs, "w") as f:
                f.write("result")

            hid = _seed_history(db, ObjectId(user_a["id"]), result_image=result_path_rel)

        resp = client.delete(f'/api/v1/history/{hid}', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200

        # Result deleted, originals preserved
        assert not os.path.exists(result_path_abs)
        assert os.path.exists(person_path)
        assert os.path.exists(clothing_path)


class TestHistoryResultAccess:
    def test_result_url_own_history(self, client, user_a, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            hid = _seed_history(db, ObjectId(user_a["id"]), result_image="results/myresult.png")

        resp = client.get(f'/api/v1/history/{hid}/result', headers=auth_header(user_a["token"]))
        assert resp.status_code == 200
        assert resp.json["data"]["result_image"] == "results/myresult.png"
        assert "url" in resp.json["data"]

    def test_result_url_unauthorized(self, client, user_a, user_b, app):
        with app.app_context():
            from app.extensions import mongo
            db = mongo.get_db()
            hid_b = _seed_history(db, ObjectId(user_b["id"]))

        resp = client.get(f'/api/v1/history/{hid_b}/result', headers=auth_header(user_a["token"]))
        assert resp.status_code == 404
