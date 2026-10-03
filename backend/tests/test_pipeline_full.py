"""
tests/test_pipeline_full.py

Integration test for the complete 2D virtual try-on pipeline.
Uses mocking to avoid running heavy AI inference in CI.
"""
import io
import os
import pytest
from unittest.mock import patch, MagicMock
from bson.objectid import ObjectId
from PIL import Image
from tests.conftest import auth_header, _make_rgb_image_bytes


def _make_clothing_in_db(db, name="Test Shirt", category="shirt"):
    """Insert a clothing record directly and return its ID."""
    img_bytes = _make_rgb_image_bytes()
    return db.clothing.insert_one({
        "name": name,
        "category": category,
        "price": 999.0,
        "color": "blue",
        "sizes": ["M"],
        "available": True,
        "image": None,  # no image initially
    }).inserted_id


def _make_processed_person_image(upload_root):
    """Create a fake processed person image at the expected path."""
    path = os.path.join(upload_root, "processed", "users", "test_person.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new("RGB", (400, 600), color=(200, 180, 160))
    img.save(path)
    return "processed/users/test_person.png", path


def _make_fake_garment_image(upload_root, subpath="clothing/catalog/test_garment.png"):
    path = os.path.join(upload_root, subpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new("RGBA", (300, 400), color=(100, 149, 237, 255))
    img.save(path)
    return subpath, path


class TestPipelineMocked:
    """Pipeline tests using mocked AI modules to test orchestration logic only."""

    def _full_mock_run(self, client, user, app, db):
        upload_root = app.config["UPLOAD_FOLDER"]
        person_rel, person_abs = _make_processed_person_image(upload_root)

        # Insert clothing with image
        garment_rel, garment_abs = _make_fake_garment_image(upload_root)
        cid = db.clothing.insert_one({
            "name": "Mock Shirt",
            "category": "shirt",
            "price": 500,
            "color": "blue",
            "sizes": ["M"],
            "available": True,
            "image": garment_rel,
        }).inserted_id

        # Create a fake result image
        results_dir = os.path.join(upload_root, "results")
        os.makedirs(results_dir, exist_ok=True)
        result_img = Image.new("RGB", (400, 600), color=(200, 180, 160))
        result_path = os.path.join(results_dir, "mock_result.png")
        result_img.save(result_path)
        result_rel = "results/mock_result.png"

        mock_pose = {
            "person_detected": True,
            "landmarks": [],
            "important_landmarks": {
                "LEFT_SHOULDER": {"x": 0.3, "y": 0.3, "visibility": 0.99, "visible": True},
                "RIGHT_SHOULDER": {"x": 0.7, "y": 0.3, "visibility": 0.99, "visible": True},
                "LEFT_HIP": {"x": 0.35, "y": 0.6, "visibility": 0.95, "visible": True},
                "RIGHT_HIP": {"x": 0.65, "y": 0.6, "visibility": 0.95, "visible": True},
            },
            "detection_quality": {"overall": "good"},
            "image_width": 400,
            "image_height": 600,
        }
        mock_body = {
            "shoulder_width_px": 160,
            "hip_width_px": 120,
            "torso_height_px": 180,
            "shoulder_center": {"x": 0.5, "y": 0.3},
        }
        mock_garment = {
            "clothing_id": str(cid),
            "source_type": "catalog",
            "category": "shirt",
            "processed_image": garment_rel,
            "geometry": {
                "bbox": {"x": 10, "y": 10, "width": 280, "height": 380},
                "center": {"x": 150, "y": 200},
                "garment_width": 280,
                "garment_height": 380,
                "aspect_ratio": 280 / 380,
            },
        }
        mock_alignment = {
            "aligned_garment": garment_rel,
            "transformation": {"scale": 1.0, "angle": 0, "tx": 0, "ty": 0},
        }
        mock_composite = {
            "result_image": result_rel,
            "image_size": {"width": 400, "height": 600},
        }

        with patch("app.services.pipeline_service.detect_pose", return_value=mock_pose), \
             patch("app.services.pipeline_service.analyse_body", return_value=mock_body), \
             patch("app.services.pipeline_service.process_garment", return_value=mock_garment), \
             patch("app.services.pipeline_service.align_garment", return_value=mock_alignment), \
             patch("app.services.pipeline_service.composite_tryon", return_value=mock_composite):

            resp = client.post('/api/v1/tryon',
                               headers=auth_header(user["token"]),
                               json={"person_image_id": person_rel, "clothing_id": str(cid)})
        return resp, str(cid)

    def test_pipeline_returns_200_and_history(self, client, user_a, app, db):
        with app.app_context():
            from app.extensions import mongo
            _db = mongo.get_db()
            resp, cid = self._full_mock_run(client, user_a, app, _db)

        assert resp.status_code == 200
        assert resp.json["success"] is True
        assert "result_id" in resp.json["data"]
        assert "result_image" in resp.json["data"]

    def test_pipeline_creates_history_record(self, client, user_a, app, db):
        with app.app_context():
            from app.extensions import mongo
            _db = mongo.get_db()
            resp, cid = self._full_mock_run(client, user_a, app, _db)

        result_id = resp.json["data"]["result_id"]

        # Verify history was created
        hist_resp = client.get(f'/api/v1/history/{result_id}', headers=auth_header(user_a["token"]))
        assert hist_resp.status_code == 200
        assert hist_resp.json["data"]["id"] == result_id

    def test_pipeline_missing_params(self, client, user_a):
        resp = client.post('/api/v1/tryon', headers=auth_header(user_a["token"]), json={})
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "MISSING_PARAMS"

    def test_pipeline_invalid_person_image(self, client, user_a):
        resp = client.post('/api/v1/tryon',
                           headers=auth_header(user_a["token"]),
                           json={"person_image_id": "../../etc/evil", "clothing_id": str(ObjectId())})
        assert resp.status_code == 400
        assert resp.json["error"]["code"] in ("INVALID_PERSON_IMAGE", "MISSING_PARAMS", "TRYON_PIPELINE_FAILED")

    def test_pipeline_nonexistent_person_file(self, client, user_a):
        resp = client.post('/api/v1/tryon',
                           headers=auth_header(user_a["token"]),
                           json={"person_image_id": "processed/users/nonexistent.png",
                                 "clothing_id": str(ObjectId())})
        assert resp.status_code == 404
        assert resp.json["error"]["code"] == "PERSON_IMAGE_NOT_FOUND"

    def test_pipeline_nonexistent_clothing(self, client, user_a, app):
        with app.app_context():
            upload_root = app.config["UPLOAD_FOLDER"]
            person_rel, _ = _make_processed_person_image(upload_root)

        resp = client.post('/api/v1/tryon',
                           headers=auth_header(user_a["token"]),
                           json={"person_image_id": person_rel,
                                 "clothing_id": str(ObjectId())})
        assert resp.status_code == 404
        assert resp.json["error"]["code"] == "CLOTHING_NOT_FOUND"

    def test_pipeline_other_users_custom_clothing_forbidden(self, client, user_a, user_b, app, db):
        with app.app_context():
            from app.extensions import mongo
            _db = mongo.get_db()
            upload_root = app.config["UPLOAD_FOLDER"]
            person_rel, _ = _make_processed_person_image(upload_root)

            # B uploads custom clothing
            b_cid = _db.user_clothing.insert_one({
                "user_id": ObjectId(user_b["id"]),
                "name": "B's Garment",
                "category": "shirt",
                "image": "clothing/user/bgarment.png",
                "available": True,
            }).inserted_id

        # A tries to use B's clothing
        resp = client.post('/api/v1/tryon',
                           headers=auth_header(user_a["token"]),
                           json={"person_image_id": person_rel,
                                 "clothing_id": str(b_cid)})
        assert resp.status_code == 403
        assert resp.json["error"]["code"] == "UNAUTHORIZED_CLOTHING"

    def test_pipeline_unauthenticated(self, client):
        resp = client.post('/api/v1/tryon', json={"person_image_id": "p", "clothing_id": "c"})
        assert resp.status_code == 401
