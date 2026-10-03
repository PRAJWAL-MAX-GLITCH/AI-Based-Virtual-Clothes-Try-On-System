"""
tests/test_uploads_full.py
Full upload tests for person images and custom clothing.
"""
import io
import pytest
from tests.conftest import auth_header, _make_rgb_image_bytes, _make_rgba_image_bytes, _make_jpeg_bytes


def _upload_person_image(client, token, image_data=None, filename="person.png", content_type="image/png"):
    data = image_data or _make_rgb_image_bytes()
    return client.post(
        '/api/v1/uploads/user-image',
        headers=auth_header(token),
        data={"image": (io.BytesIO(data), filename, content_type)},
        content_type="multipart/form-data"
    )


def _upload_custom_clothing(client, token, image_data=None, category="shirt",
                            filename="garment.png", content_type="image/png"):
    data = image_data or _make_rgb_image_bytes()
    
    kwargs = {
        "data": {
            "image": (io.BytesIO(data), filename, content_type),
            "category": category
        },
        "content_type": "multipart/form-data"
    }
    
    if token:
        kwargs["headers"] = auth_header(token)

    return client.post('/api/v1/user-clothing', **kwargs)


class TestPersonImageUpload:
    def test_authenticated_can_upload_png(self, client, user_a):
        token = user_a["token"]
        img_bytes = _make_rgb_image_bytes()
        data = {"image": (io.BytesIO(img_bytes), "test.png")}
        resp = client.post('/api/v1/uploads/user-image', headers=auth_header(token), data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        assert resp.json["success"] is True
        assert "path" in resp.json["data"]

    def test_authenticated_can_upload_jpeg(self, client, user_a):
        token = user_a["token"]
        img_bytes = _make_jpeg_bytes()
        data = {"image": (io.BytesIO(img_bytes), "test.jpg")}
        resp = client.post('/api/v1/uploads/user-image', headers=auth_header(token), data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        assert resp.json["success"] is True

    def test_unauthenticated_cannot_upload(self, client):
        img_bytes = _make_rgb_image_bytes()
        data = {"image": (io.BytesIO(img_bytes), "test.png")}
        resp = client.post('/api/v1/uploads/user-image', data=data, content_type='multipart/form-data')
        assert resp.status_code == 401

    def test_corrupt_image_rejected(self, client, user_a):
        token = user_a["token"]
        data = {"image": (io.BytesIO(b"not_an_image"), "test.png")}
        resp = client.post('/api/v1/uploads/user-image', headers=auth_header(token), data=data, content_type='multipart/form-data')
        assert resp.status_code == 400
        assert resp.json["error"]["code"] == "CORRUPTED_IMAGE"

    def test_original_filename_not_trusted(self, client, user_a):
        token = user_a["token"]
        data = {"image": (io.BytesIO(_make_rgb_image_bytes()), "../../../etc/passwd.png")}
        resp = client.post('/api/v1/uploads/user-image', headers=auth_header(token), data=data, content_type='multipart/form-data')
        assert resp.status_code == 200
        assert "../" not in resp.json["data"]["path"]

    def test_no_file_field(self, client, user_a):
        resp = client.post('/api/v1/uploads/user-image',
                           headers=auth_header(user_a["token"]),
                           data={},
                           content_type="multipart/form-data")
        assert resp.status_code == 400

    def test_unsupported_extension_rejected(self, client, user_a):
        resp = _upload_person_image(
            client, user_a["token"],
            image_data=_make_rgb_image_bytes(), filename="person.bmp", content_type="image/bmp"
        )
        assert resp.status_code == 400


class TestCustomClothingUpload:
    def test_valid_upload(self, client, user_a):
        resp = _upload_custom_clothing(client, user_a["token"])
        assert resp.status_code == 201
        data = resp.json["data"]["clothing"]
        assert "id" in data
        assert data["category"] == "shirt"

    def test_rgba_upload(self, client, user_a):
        resp = _upload_custom_clothing(
            client, user_a["token"], image_data=_make_rgba_image_bytes(),
            filename="trans.png", content_type="image/png"
        )
        assert resp.status_code == 201
        assert "id" in resp.json["data"]["clothing"]

    def test_all_valid_categories(self, client, user_a):
        for cat in ["t-shirt", "shirt", "hoodie", "jacket", "dress", "top"]:
            resp = _upload_custom_clothing(client, user_a["token"], category=cat)
            assert resp.status_code == 201

    def test_invalid_category(self, client, user_a):
        resp = _upload_custom_clothing(client, user_a["token"], category="cars")
        assert resp.status_code == 400

    def test_corrupt_image_rejected(self, client, user_a):
        resp = _upload_custom_clothing(client, user_a["token"], image_data=b"garbage")
        assert resp.status_code == 400

    def test_unauthenticated_cannot_upload(self, client):
        resp = _upload_custom_clothing(client, token=None)
        assert resp.status_code == 401


class TestCustomClothingOwnership:
    def test_user_lists_own_clothing(self, client, user_a, user_b):
        _upload_custom_clothing(client, user_a["token"])
        _upload_custom_clothing(client, user_a["token"])
        _upload_custom_clothing(client, user_b["token"])

        resp_a = client.get('/api/v1/user-clothing', headers=auth_header(user_a["token"]))
        assert resp_a.status_code == 200
        assert len(resp_a.json["data"]["items"]) == 2
        
        a_ids = {i["id"] for i in resp_a.json["data"]["items"]}
        
        resp_b = client.get('/api/v1/user-clothing', headers=auth_header(user_b["token"]))
        b_ids = {i["id"] for i in resp_b.json["data"]["items"]}
        assert len(b_ids) == 1
        assert a_ids.isdisjoint(b_ids)

    def test_user_a_cannot_get_user_b_clothing(self, client, user_a, user_b):
        resp_b = _upload_custom_clothing(client, user_b["token"])
        b_clothing_id = resp_b.json["data"]["clothing"]["id"]

        resp_a = client.get(f'/api/v1/user-clothing/{b_clothing_id}', headers=auth_header(user_a["token"]))
        assert resp_a.status_code == 404

    def test_user_a_cannot_delete_user_b_clothing(self, client, user_a, user_b):
        resp_b = _upload_custom_clothing(client, user_b["token"])
        b_clothing_id = resp_b.json["data"]["clothing"]["id"]

        resp_a = client.delete(f'/api/v1/user-clothing/{b_clothing_id}', headers=auth_header(user_a["token"]))
        assert resp_a.status_code == 404

    def test_user_can_delete_own_clothing(self, client, user_a):
        resp = _upload_custom_clothing(client, user_a["token"])
        cid = resp.json["data"]["clothing"]["id"]

        del_resp = client.delete(f'/api/v1/user-clothing/{cid}', headers=auth_header(user_a["token"]))
        assert del_resp.status_code == 200

        # Verify gone
        get_resp = client.get(f'/api/v1/user-clothing/{cid}', headers=auth_header(user_a["token"]))
        assert get_resp.status_code == 404
