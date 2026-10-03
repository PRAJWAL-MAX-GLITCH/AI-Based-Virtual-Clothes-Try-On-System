"""
tests/conftest.py

Shared fixtures for the entire test suite.

Database isolation:
  - Tests run against a dedicated 'virtual_try_on_test' database.
  - Each session gets a fresh DB; critical collections are wiped between tests
    via the `clean_db` fixture.
  - No production data is touched.
"""

import io
import os
import datetime
import pytest
import jwt
from bson.objectid import ObjectId
from PIL import Image
from werkzeug.security import generate_password_hash

# ─────────────────────────────────────────────────────────────────────────────
# App & Client
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    """Create a Flask test application pointing at the TEST database."""
    from app import create_app, init_db_indexes
    application = create_app('development')
    application.config.update({
        "TESTING": True,
        "MONGO_DB_NAME": "virtual_try_on_test",   # isolated test DB
        "MONGO_URI": "mongodb://localhost:27017/virtual_try_on_test",
        "JWT_SECRET_KEY": "test-jwt-secret",
        "MAX_CONTENT_LENGTH": 5 * 1024 * 1024,
    })
    # Re-initialize mongo so it points to the isolated TEST database
    with application.app_context():
        from app.extensions import mongo
        mongo.init_app(application)   # re-run with updated config
    # Re-create indexes in the test database
    init_db_indexes(application)
    yield application


@pytest.fixture
def app_ctx(app):
    """Push an application context for each test."""
    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def client(app):
    """Session-scoped Flask test client."""
    return app.test_client()


# ─────────────────────────────────────────────────────────────────────────────
# Database helpers
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def db(app):
    """Return a handle to the test MongoDB database."""
    with app.app_context():
        from app.extensions import mongo
        return mongo.get_db()


@pytest.fixture(autouse=False)
def clean_db(db):
    """
    Wipe critical collections before and after each test that requests this
    fixture.  Pass `clean_db` as a parameter to opt-in.
    """
    _wipe(db)
    yield
    _wipe(db)


def _wipe(db):
    for col in ("users", "clothing", "user_clothing", "tryon_history"):
        db[col].delete_many({})


# ─────────────────────────────────────────────────────────────────────────────
# User factories
# ─────────────────────────────────────────────────────────────────────────────

JWT_SECRET = "test-jwt-secret"


def _make_token(user_id: ObjectId) -> str:
    now = datetime.datetime.now(datetime.timezone.utc)
    return jwt.encode(
        {"sub": str(user_id), "iat": now, "exp": now + datetime.timedelta(hours=2)},
        JWT_SECRET,
        algorithm="HS256",
    )


def _insert_user(db, email: str, role: str = "user", is_active: bool = True) -> tuple:
    doc = {
        "_id": ObjectId(),
        "email": email,
        "name": email.split("@")[0].replace(".", " ").title(),
        "password_hash": generate_password_hash("Password123!"),
        "role": role,
        "is_active": is_active,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "updated_at": datetime.datetime.now(datetime.timezone.utc),
    }
    db.users.insert_one(doc)
    token = _make_token(doc["_id"])
    return doc, token


@pytest.fixture()
def user_a(db, clean_db, app):
    """Normal test user A — fresh DB state."""
    with app.app_context():
        from app.extensions import mongo
        _db = mongo.get_db()
        doc, token = _insert_user(_db, "user_a@test.com", role="user")
        return {"doc": doc, "token": token, "id": str(doc["_id"])}


@pytest.fixture()
def user_b(db, clean_db, app):
    """Normal test user B — same clean DB as user_a."""
    with app.app_context():
        from app.extensions import mongo
        _db = mongo.get_db()
        doc, token = _insert_user(_db, "user_b@test.com", role="user")
        return {"doc": doc, "token": token, "id": str(doc["_id"])}


@pytest.fixture()
def admin_user(db, clean_db, app):
    """Admin test user."""
    with app.app_context():
        from app.extensions import mongo
        _db = mongo.get_db()
        doc, token = _insert_user(_db, "admin@test.com", role="admin")
        return {"doc": doc, "token": token, "id": str(doc["_id"])}


@pytest.fixture()
def inactive_user(db, clean_db, app):
    """Inactive (deactivated) user."""
    with app.app_context():
        from app.extensions import mongo
        _db = mongo.get_db()
        doc, token = _insert_user(_db, "inactive@test.com", role="user", is_active=False)
        return {"doc": doc, "token": token, "id": str(doc["_id"])}


# ─────────────────────────────────────────────────────────────────────────────
# Sample image helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_rgb_image_bytes(width=200, height=300, color=(100, 149, 237)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _make_rgba_image_bytes(width=200, height=300) -> bytes:
    img = Image.new("RGBA", (width, height), color=(100, 149, 237, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def _make_jpeg_bytes(width=200, height=300) -> bytes:
    img = Image.new("RGB", (width, height), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


@pytest.fixture()
def sample_png_image():
    return _make_rgb_image_bytes()


@pytest.fixture()
def sample_jpeg_image():
    return _make_jpeg_bytes()


@pytest.fixture()
def sample_rgba_image():
    return _make_rgba_image_bytes()


@pytest.fixture()
def corrupt_image():
    return b"this is not an image at all"


# ─────────────────────────────────────────────────────────────────────────────
# Auth header helper
# ─────────────────────────────────────────────────────────────────────────────

def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
