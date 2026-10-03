import pytest
import os

@pytest.fixture
def setup_db(app):
    with app.app_context():
        from app.extensions import mongo
        db = mongo.get_db()
        from werkzeug.security import generate_password_hash
        db.users.delete_many({})
        u1 = db.users.insert_one({"email": "u1@test.com", "password_hash": generate_password_hash("pass"), "role": "user"}).inserted_id
        u2 = db.users.insert_one({"email": "u2@test.com", "password_hash": generate_password_hash("pass"), "role": "user"}).inserted_id

        # Create clothing records
        db.clothing.delete_many({})
        db.user_clothing.delete_many({})

        cat_id = db.clothing.insert_one({"category": "shirt", "image": "clothing/catalog/cat.png"}).inserted_id
        u1_cloth_id = db.user_clothing.insert_one({"user_id": u1, "category": "hoodie", "image": "clothing/user/u1.png"}).inserted_id

        # Tokens
        import jwt
        import datetime
        secret = app.config.get('JWT_SECRET_KEY', 'test_secret')
        def _gen_token(uid):
            now = datetime.datetime.now(datetime.timezone.utc)
            return jwt.encode({"sub": str(uid), "iat": now, "exp": now + datetime.timedelta(hours=1)}, secret, algorithm="HS256")
            
        return {
            "u1_token": _gen_token(u1),
            "u2_token": _gen_token(u2),
            "cat_id": str(cat_id),
            "u1_cloth_id": str(u1_cloth_id)
        }

def test_align_garment_unauthenticated(client):
    response = client.post('/api/v1/processing/align-garment', json={})
    assert response.status_code == 401

def test_align_garment_missing_params(client, setup_db):
    tokens = setup_db
    response = client.post('/api/v1/processing/align-garment', 
                           headers={"Authorization": f"Bearer {tokens['u1_token']}"},
                           json={"person_image_id": "processed/users/test.png"})
    assert response.status_code == 400
    assert response.json["error"]["code"] == "MISSING_PARAMS"

def test_align_garment_invalid_path(client, setup_db):
    tokens = setup_db
    response = client.post('/api/v1/processing/align-garment', 
                           headers={"Authorization": f"Bearer {tokens['u1_token']}"},
                           json={"person_image_id": "../etc/passwd", "clothing_id": tokens["cat_id"]})
    assert response.status_code == 400
    assert response.json["error"]["code"] == "INVALID_PERSON_REFERENCE"

def test_align_garment_unauthorized_custom_clothing(client, setup_db, app):
    tokens = setup_db
    import os
    from PIL import Image
    upload_root = app.config['UPLOAD_FOLDER']
    person_dir = os.path.join(upload_root, 'processed', 'users')
    os.makedirs(person_dir, exist_ok=True)
    person_path = os.path.join(person_dir, 'test.png')
    Image.new('RGB', (100, 100), color=(255, 0, 0)).save(person_path)

    # u2 tries to access u1's clothing
    response = client.post('/api/v1/processing/align-garment',
                           headers={"Authorization": f"Bearer {tokens['u2_token']}"},
                           json={"person_image_id": "processed/users/test.png", "clothing_id": tokens["u1_cloth_id"]})
    assert response.status_code == 403
    assert response.json["error"]["code"] == "FORBIDDEN"
