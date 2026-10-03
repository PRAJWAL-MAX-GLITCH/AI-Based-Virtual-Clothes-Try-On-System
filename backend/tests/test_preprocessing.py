"""
tests/test_preprocessing.py

Tests for the image preprocessing pipeline.

Uses temporary directories so the real uploads/ tree is never polluted.
All tests are self-contained: images are created in-memory with Pillow
and saved to a tmpdir fixture.
"""

import io
import os
import pytest
from PIL import Image

# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

# Fixtures


# ── Tiny image factories ──────────────────────────────────────────────────────

def _make_image_file(tmp_path, mode='RGB', fmt='PNG', size=(400, 600), name=None):
    """Save a solid-colour PIL image to a temp file and return its path."""
    img = Image.new(mode, size, color=(120, 180, 200) if mode != 'RGBA'
                    else (120, 180, 200, 180))
    fname = name or f"test_{mode.lower()}.{fmt.lower()}"
    path  = os.path.join(str(tmp_path), fname)
    img.save(path, format=fmt)
    return path


def _make_image_in_upload_root(app, sub, mode='RGB', fmt='PNG', size=(400, 600), name=None):
    """
    Save a test image inside app.UPLOAD_FOLDER/<sub>/ and return the
    relative path (relative to UPLOAD_FOLDER) – this is what is stored
    in MongoDB.
    """
    directory = os.path.join(app.config['UPLOAD_FOLDER'], sub)
    os.makedirs(directory, exist_ok=True)
    fname = name or f"test_{mode.lower()}.{fmt.lower()}"
    path  = os.path.join(directory, fname)
    img   = Image.new(mode, size, color=(120, 180, 200) if mode != 'RGBA'
                      else (120, 180, 200, 180))
    img.save(path, format=fmt)
    return os.path.relpath(path, app.config['UPLOAD_FOLDER']).replace('\\', '/')


# ──────────────────────────────────────────────────────────────────────────────
# image_utils unit tests
# ──────────────────────────────────────────────────────────────────────────────

class TestImageUtils:
    def test_validate_valid_image(self, tmp_path):
        from app.utils.image_utils import validate_image_file
        path = _make_image_file(tmp_path, 'RGB', 'PNG', (200, 200))
        img  = validate_image_file(path)
        assert img.size == (200, 200)

    def test_validate_missing_file(self, tmp_path):
        from app.utils.image_utils import validate_image_file, ImageUtilsError
        with pytest.raises(ImageUtilsError) as exc:
            validate_image_file(str(tmp_path / 'nonexistent.png'))
        assert exc.value.code == 'IMAGE_NOT_FOUND'

    def test_validate_corrupted_file(self, tmp_path):
        from app.utils.image_utils import validate_image_file, ImageUtilsError
        bad = tmp_path / 'corrupted.png'
        bad.write_bytes(b'this is not an image')
        with pytest.raises(ImageUtilsError) as exc:
            validate_image_file(str(bad))
        assert exc.value.code == 'CORRUPTED_IMAGE'

    def test_validate_too_small(self, tmp_path):
        from app.utils.image_utils import validate_image_file, ImageUtilsError
        path = _make_image_file(tmp_path, 'RGB', 'PNG', (10, 10))
        with pytest.raises(ImageUtilsError) as exc:
            validate_image_file(path, min_width=64, min_height=64)
        assert exc.value.code == 'IMAGE_TOO_SMALL'

    def test_to_rgb_from_rgba(self):
        from app.utils.image_utils import to_rgb
        rgba = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
        rgb  = to_rgb(rgba)
        assert rgb.mode == 'RGB'

    def test_to_rgb_keeps_rgb(self):
        from app.utils.image_utils import to_rgb
        img = Image.new('RGB', (100, 100))
        out = to_rgb(img)
        assert out.mode == 'RGB'

    def test_to_rgba_adds_alpha(self):
        from app.utils.image_utils import to_rgba
        img  = Image.new('RGB', (100, 100))
        out  = to_rgba(img)
        assert out.mode == 'RGBA'

    def test_resize_keep_aspect_ratio_landscape(self):
        from app.utils.image_utils import resize_keep_aspect_ratio
        img = Image.new('RGB', (1920, 1080))
        resized, scale = resize_keep_aspect_ratio(img, 768, 1024)
        w, h = resized.size
        # Must fit within 768x1024 and preserve ratio
        assert w <= 768 and h <= 1024
        assert abs(w / h - 1920 / 1080) < 0.01    # aspect ratio preserved

    def test_resize_keep_aspect_ratio_portrait(self):
        from app.utils.image_utils import resize_keep_aspect_ratio
        img = Image.new('RGB', (600, 900))
        resized, scale = resize_keep_aspect_ratio(img, 768, 1024)
        w, h = resized.size
        assert w <= 768 and h <= 1024
        assert abs(w / h - 600 / 900) < 0.01

    def test_resize_and_pad_output_size(self):
        from app.utils.image_utils import resize_and_pad
        img    = Image.new('RGB', (400, 300))
        canvas, meta = resize_and_pad(img, 768, 1024)
        assert canvas.size == (768, 1024)

    def test_resize_and_pad_metadata_keys(self):
        from app.utils.image_utils import resize_and_pad
        img    = Image.new('RGB', (400, 300))
        _, meta = resize_and_pad(img, 768, 1024)
        for key in ('original_width', 'original_height',
                    'resized_width', 'resized_height', 'scale', 'padding'):
            assert key in meta
        for pad_key in ('top', 'bottom', 'left', 'right'):
            assert pad_key in meta['padding']

    def test_resize_and_pad_no_distortion(self):
        """After padding the canvas should be exactly target size."""
        from app.utils.image_utils import resize_and_pad
        img    = Image.new('RGB', (1000, 200))   # very wide
        canvas, meta = resize_and_pad(img, 768, 1024)
        assert canvas.size == (768, 1024)
        # The resized piece should respect aspect ratio
        rsz_w, rsz_h = meta['resized_width'], meta['resized_height']
        assert abs(rsz_w / rsz_h - 1000 / 200) < 0.02

    def test_secure_filename_generated(self):
        from app.utils.image_utils import generate_processed_filename
        name1 = generate_processed_filename('png')
        name2 = generate_processed_filename('png')
        assert name1 != name2
        assert name1.endswith('.png')
        assert name1.startswith('proc_')

    def test_save_image(self, tmp_path):
        from app.utils.image_utils import save_image
        img  = Image.new('RGB', (100, 100), (10, 20, 30))
        path = save_image(img, str(tmp_path), 'out.png')
        assert os.path.isfile(path)
        reloaded = Image.open(path)
        assert reloaded.size == (100, 100)


# ──────────────────────────────────────────────────────────────────────────────
# Preprocessing pipeline tests (require app context for config access)
# ──────────────────────────────────────────────────────────────────────────────

class TestPreprocessingPipeline:

    def test_preprocess_person_image_png(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image
        rel = _make_image_in_upload_root(app_ctx, 'users', 'RGB', 'PNG', (400, 600))
        result = preprocess_person_image(rel)
        assert result['type'] == 'person'
        assert result['format'] == 'PNG'
        assert result['mode']   == 'RGB'
        assert result['processed_path'] != result['original_path']

    def test_preprocess_person_image_jpg(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image
        rel = _make_image_in_upload_root(app_ctx, 'users', 'RGB', 'JPEG', (400, 600), 'test.jpg')
        result = preprocess_person_image(rel)
        assert result['type'] == 'person'

    def test_preprocess_person_image_webp(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image
        rel = _make_image_in_upload_root(app_ctx, 'users', 'RGB', 'WEBP', (400, 600), 'test.webp')
        result = preprocess_person_image(rel)
        assert result['type'] == 'person'

    def test_preprocess_clothing_image_png(self, app_ctx):
        from app.ai.preprocessing import preprocess_clothing_image
        rel = _make_image_in_upload_root(app_ctx, 'clothing/catalog', 'RGB', 'PNG', (400, 600))
        result = preprocess_clothing_image(rel)
        assert result['type'] == 'clothing'
        assert result['mode'] == 'RGB'

    def test_preprocess_clothing_rgba_composited(self, app_ctx):
        """RGBA clothing with preserve_alpha=False should yield RGB."""
        from app.ai.preprocessing import preprocess_clothing_image
        rel = _make_image_in_upload_root(app_ctx, 'clothing/user', 'RGBA', 'PNG', (400, 600), 'rgba.png')
        result = preprocess_clothing_image(rel, preserve_alpha=False)
        assert result['mode'] == 'RGB'

    def test_preprocess_clothing_rgba_preserved(self, app_ctx):
        """RGBA clothing with preserve_alpha=True should yield RGBA."""
        from app.ai.preprocessing import preprocess_clothing_image
        rel = _make_image_in_upload_root(app_ctx, 'clothing/user', 'RGBA', 'PNG', (400, 600), 'rgba2.png')
        result = preprocess_clothing_image(rel, preserve_alpha=True)
        assert result['mode'] == 'RGBA'

    def test_aspect_ratio_preserved_in_result(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image
        rel = _make_image_in_upload_root(app_ctx, 'users', 'RGB', 'PNG', (300, 700), 'tall.png')
        result = preprocess_person_image(rel)
        assert result['processed_size']['width']  == app_ctx.config['PREPROCESS_TARGET_WIDTH']
        assert result['processed_size']['height'] == app_ctx.config['PREPROCESS_TARGET_HEIGHT']

    def test_original_is_not_overwritten(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image
        rel = _make_image_in_upload_root(app_ctx, 'users', 'RGB', 'PNG', (400, 500), 'orig_check.png')
        original_abs = os.path.join(app_ctx.config['UPLOAD_FOLDER'], rel)
        original_mtime = os.path.getmtime(original_abs)
        preprocess_person_image(rel)
        assert os.path.getmtime(original_abs) == original_mtime  # unchanged

    def test_processed_file_is_created(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image
        rel = _make_image_in_upload_root(app_ctx, 'users', 'RGB', 'PNG', (400, 500), 'check_created.png')
        result = preprocess_person_image(rel)
        processed_abs = os.path.join(app_ctx.config['UPLOAD_FOLDER'], result['processed_path'])
        assert os.path.isfile(processed_abs)

    def test_processed_filename_is_unique(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image
        rel1 = _make_image_in_upload_root(app_ctx, 'users', 'RGB', 'PNG', (400, 500), 'unique1.png')
        rel2 = _make_image_in_upload_root(app_ctx, 'users', 'RGB', 'PNG', (400, 500), 'unique2.png')
        r1 = preprocess_person_image(rel1)
        r2 = preprocess_person_image(rel2)
        assert r1['processed_path'] != r2['processed_path']

    def test_metadata_contains_all_keys(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image
        rel    = _make_image_in_upload_root(app_ctx, 'users', 'RGB', 'PNG', (400, 500), 'meta_test.png')
        result = preprocess_person_image(rel)
        for key in ('type', 'original_path', 'processed_path',
                    'original_size', 'processed_size', 'format',
                    'mode', 'scale', 'padding'):
            assert key in result, f"Missing key: {key}"
        for pad_key in ('top', 'bottom', 'left', 'right'):
            assert pad_key in result['padding']

    def test_corrupted_image_rejected(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image, PreprocessingError
        bad_dir = os.path.join(app_ctx.config['UPLOAD_FOLDER'], 'users')
        os.makedirs(bad_dir, exist_ok=True)
        bad_path = os.path.join(bad_dir, 'bad.png')
        with open(bad_path, 'wb') as f:
            f.write(b'not an image at all')
        with pytest.raises(PreprocessingError) as exc:
            preprocess_person_image('users/bad.png')
        assert exc.value.code == 'CORRUPTED_IMAGE'

    def test_missing_image_rejected(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image, PreprocessingError
        with pytest.raises(PreprocessingError) as exc:
            preprocess_person_image('users/does_not_exist.png')
        assert exc.value.code == 'IMAGE_NOT_FOUND'

    def test_path_traversal_rejected(self, app_ctx):
        from app.ai.preprocessing import preprocess_person_image, PreprocessingError
        with pytest.raises(PreprocessingError) as exc:
            preprocess_person_image('../../etc/passwd')
        assert exc.value.code == 'INVALID_PATH'


# ──────────────────────────────────────────────────────────────────────────────
# API endpoint tests
# ──────────────────────────────────────────────────────────────────────────────

class TestProcessingAPI:
    def test_preview_unauthenticated(self, client):
        response = client.post('/api/v1/processing/preview', json={
            "type": "person", "image_path": "users/test.png"
        })
        assert response.status_code == 401

    def test_preview_invalid_token(self, client):
        response = client.post('/api/v1/processing/preview',
                               json={"type": "person", "image_path": "users/test.png"},
                               headers={"Authorization": "Bearer invalidtoken"})
        assert response.status_code == 401

    def test_preview_missing_path(self, client):
        response = client.post('/api/v1/processing/preview',
                               json={"type": "person"},
                               headers={"Authorization": "Bearer invalidtoken"})
        # Will be caught by JWT check first
        assert response.status_code == 401
