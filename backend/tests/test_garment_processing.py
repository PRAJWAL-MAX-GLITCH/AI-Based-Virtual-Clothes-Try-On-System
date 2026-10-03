"""
tests/test_garment_processing.py

Tests for garment image processing and the associated API endpoint.
Includes pure logic tests for bounding box generation and integration tests
for the /garment endpoint, ensuring proper ownership rules are enforced.
"""

import os
import json
import pytest
from PIL import Image
from bson.objectid import ObjectId

from app.ai.garment_processing import (
    _find_content_bounding_box,
    process_garment,
    GarmentProcessingError
)

# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

# Fixtures

# Image helpers
def _create_test_image(directory: str, mode: str, color: tuple, size=(200, 200), name="test.png") -> str:
    """Create a solid color image for testing."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name)
    Image.new(mode, size, color).save(path)
    return path

def _create_centered_box_image(directory: str, name="box.png") -> str:
    """
    Creates a 100x100 RGB image with a white background and a
    black 50x50 square in the center.
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name)
    img = Image.new('RGB', (100, 100), (255, 255, 255))
    # Draw a 50x50 black box from (25,25) to (74,74)
    for y in range(25, 75):
        for x in range(25, 75):
            img.putpixel((x, y), (0, 0, 0))
    img.save(path)
    return path

def _create_rgba_content_image(directory: str, name="rgba.png") -> str:
    """
    Creates a 100x100 RGBA image with transparent background (alpha=0)
    and a solid opaque 50x50 square in the center (alpha=255).
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name)
    img = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
    for y in range(25, 75):
        for x in range(25, 75):
            img.putpixel((x, y), (255, 0, 0, 255))
    img.save(path)
    return path


# ──────────────────────────────────────────────────────────────────────────────
# Unit Tests for Bounding Box Logic
# ──────────────────────────────────────────────────────────────────────────────

class TestGarmentBoundingBox:

    def test_rgb_content_detection(self, tmp_path):
        """Should detect the black box against the white background."""
        path = _create_centered_box_image(str(tmp_path))
        bbox = _find_content_bounding_box(path, pad_color=(255, 255, 255))
        assert bbox["x_min"] == pytest.approx(0.25, abs=0.02)
        assert bbox["y_min"] == pytest.approx(0.25, abs=0.02)
        assert bbox["x_max"] == pytest.approx(0.75, abs=0.02)
        assert bbox["y_max"] == pytest.approx(0.75, abs=0.02)

    def test_rgba_content_detection(self, tmp_path):
        """Should detect the opaque content against the transparent background."""
        path = _create_rgba_content_image(str(tmp_path))
        bbox = _find_content_bounding_box(path)
        assert bbox["x_min"] == pytest.approx(0.25, abs=0.02)
        assert bbox["y_min"] == pytest.approx(0.25, abs=0.02)
        assert bbox["x_max"] == pytest.approx(0.75, abs=0.02)
        assert bbox["y_max"] == pytest.approx(0.75, abs=0.02)

    def test_empty_uniform_image_fallback(self, tmp_path):
        """Should fallback to the entire image if it's completely uniform (e.g. solid white)."""
        path = _create_test_image(str(tmp_path), 'RGB', (255, 255, 255))
        bbox = _find_content_bounding_box(path, pad_color=(255, 255, 255))
        assert bbox["x_min"] == 0.0
        assert bbox["y_min"] == 0.0
        assert bbox["x_max"] == 1.0
        assert bbox["y_max"] == 1.0


# ──────────────────────────────────────────────────────────────────────────────
# Integration Tests for process_garment service
# ──────────────────────────────────────────────────────────────────────────────

class TestGarmentProcessingService:

    def test_process_valid_garment(self, app_ctx, tmp_path):
        # 1. Create a raw uploaded image in uploads/clothing/catalog
        raw_dir = os.path.join(app_ctx.config['UPLOAD_FOLDER'], 'clothing', 'catalog')
        rel_path = 'clothing/catalog/test_shirt.png'
        _create_centered_box_image(raw_dir, 'test_shirt.png')

        # 2. Process it
        result = process_garment(
            clothing_id="507f1f77bcf86cd799439011",
            stored_relative_path=rel_path,
            source_type="catalog",
            category="shirt"
        )

        assert result["clothing_id"] == "507f1f77bcf86cd799439011"
        assert result["source_type"] == "catalog"
        assert result["category"] == "shirt"
        assert result["original_image"] == rel_path

        # It should have created a processed image
        assert result["processed_image"].startswith("processed/clothing/proc_")
        processed_abs = os.path.join(app_ctx.config['UPLOAD_FOLDER'], result["processed_image"])
        assert os.path.isfile(processed_abs)

        # Geometry checks
        geom = result["geometry"]
        assert geom["image_width"] == app_ctx.config.get('PREPROCESS_TARGET_WIDTH', 768)
        assert geom["image_height"] == app_ctx.config.get('PREPROCESS_TARGET_HEIGHT', 1024)
        assert "bounding_box" in geom
        assert "center" in geom
        assert geom["garment_width"] > 0
        assert geom["garment_height"] > 0
        assert geom["aspect_ratio"] > 0

    def test_invalid_source_type(self, app_ctx):
        with pytest.raises(GarmentProcessingError) as exc:
            process_garment("id", "path.png", "invalid_type", "shirt")
        assert exc.value.code == "INVALID_SOURCE"

    def test_missing_image(self, app_ctx):
        with pytest.raises(GarmentProcessingError) as exc:
            process_garment("id", "clothing/catalog/missing.png", "catalog", "shirt")
        assert exc.value.code == "IMAGE_NOT_FOUND"


# ──────────────────────────────────────────────────────────────────────────────
# API Endpoint Tests
# ──────────────────────────────────────────────────────────────────────────────

class TestGarmentAPI:

    @pytest.fixture
    def setup_db(self, app_ctx):
        from app.extensions import mongo
        db = mongo.get_db()
        from werkzeug.security import generate_password_hash
        db.users.delete_many({})
        u1 = db.users.insert_one({"email": "u1@test.com", "password_hash": generate_password_hash("pass"), "role": "user"}).inserted_id
        u2 = db.users.insert_one({"email": "u2@test.com", "password_hash": generate_password_hash("pass"), "role": "user"}).inserted_id

        # Setup upload dirs
        cat_dir = os.path.join(app_ctx.config['UPLOAD_FOLDER'], 'clothing', 'catalog')
        user_dir = os.path.join(app_ctx.config['UPLOAD_FOLDER'], 'clothing', 'user')
        _create_test_image(cat_dir, 'RGB', (255, 0, 0), name="cat.png")
        _create_test_image(user_dir, 'RGB', (0, 255, 0), name="u1.png")

        # Create clothing records
        db.clothing.delete_many({})
        db.user_clothing.delete_many({})

        cat_id = db.clothing.insert_one({"category": "shirt", "image": "clothing/catalog/cat.png"}).inserted_id
        u1_cloth_id = db.user_clothing.insert_one({"user_id": u1, "category": "hoodie", "image": "clothing/user/u1.png"}).inserted_id

        # Tokens
        import jwt
        import datetime
        secret = app_ctx.config.get('JWT_SECRET_KEY', 'test_secret')
        def _gen_token(uid):
            now = datetime.datetime.now(datetime.timezone.utc)
            return jwt.encode({"sub": str(uid), "iat": now, "exp": now + datetime.timedelta(hours=1)}, secret, algorithm="HS256")
            
        return {
            "u1_token": _gen_token(u1),
            "u2_token": _gen_token(u2),
            "cat_id": str(cat_id),
            "u1_cloth_id": str(u1_cloth_id)
        }

    def test_unauthenticated(self, client):
        r = client.post('/api/v1/processing/garment', json={"clothing_id": str(ObjectId())})
        assert r.status_code == 401

    def test_process_catalog_garment_success(self, client, setup_db):
        r = client.post(
            '/api/v1/processing/garment',
            json={"clothing_id": setup_db["cat_id"]},
            headers={"Authorization": f"Bearer {setup_db['u1_token']}"}
        )
        assert r.status_code == 200
        assert r.json["data"]["source_type"] == "catalog"
        assert r.json["data"]["category"] == "shirt"

    def test_process_own_custom_garment_success(self, client, setup_db):
        r = client.post(
            '/api/v1/processing/garment',
            json={"clothing_id": setup_db["u1_cloth_id"]},
            headers={"Authorization": f"Bearer {setup_db['u1_token']}"}
        )
        assert r.status_code == 200
        assert r.json["data"]["source_type"] == "user_custom"

    def test_process_others_custom_garment_forbidden(self, client, setup_db):
        r = client.post(
            '/api/v1/processing/garment',
            json={"clothing_id": setup_db["u1_cloth_id"]},
            headers={"Authorization": f"Bearer {setup_db['u2_token']}"}
        )
        assert r.status_code == 403
        assert r.json["error"]["code"] == "FORBIDDEN"

    def test_missing_clothing_id(self, client, setup_db):
        r = client.post('/api/v1/processing/garment', json={}, headers={"Authorization": f"Bearer {setup_db['u1_token']}"})
        assert r.status_code == 400

    def test_invalid_clothing_id(self, client, setup_db):
        r = client.post('/api/v1/processing/garment', json={"clothing_id": "bad-id"}, headers={"Authorization": f"Bearer {setup_db['u1_token']}"})
        assert r.status_code == 400

    def test_clothing_not_found(self, client, setup_db):
        r = client.post('/api/v1/processing/garment', json={"clothing_id": str(ObjectId())}, headers={"Authorization": f"Bearer {setup_db['u1_token']}"})
        assert r.status_code == 404
