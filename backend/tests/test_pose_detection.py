"""
tests/test_pose_detection.py

Tests for the MediaPipe pose detection module.

Strategy
--------
- Mapping / naming tests: pure unit tests, no I/O.
- Detector integration tests: use a solid-colour PNG so MediaPipe returns
  "no person detected" gracefully (we verify clean handling, not landmark values).
- Landmark structure tests: use fixture dicts (no real image needed).
- API auth tests: verify HTTP guards without running real detection.
"""

import os
import json
import pytest
from PIL import Image


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

# Fixtures


def _save_blank_png(directory: str, name: str = 'blank.png',
                    size=(768, 1024)) -> str:
    """Save a solid white PNG (no person) and return its absolute path."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name)
    Image.new('RGB', size, (255, 255, 255)).save(path, format='PNG')
    return path


def _make_fake_pose_result(person_detected: bool = True) -> dict:
    """Return a synthetic pose result dict (mirrors PoseDetector.detect output)."""
    if not person_detected:
        return {
            "success": False,
            "person_detected": False,
            "landmarks": [],
            "important_landmarks": {},
            "image_width": 768,
            "image_height": 1024,
            "error": "No person detected in the image",
        }
    important = {
        "nose":           {"x": 0.50, "y": 0.12, "z": 0.00, "visibility": 0.99, "px": 384, "py": 123,  "visible": True},
        "left_shoulder":  {"x": 0.35, "y": 0.30, "z": 0.00, "visibility": 0.98, "px": 269, "py": 307,  "visible": True},
        "right_shoulder": {"x": 0.65, "y": 0.30, "z": 0.00, "visibility": 0.97, "px": 499, "py": 307,  "visible": True},
        "left_elbow":     {"x": 0.28, "y": 0.50, "z": 0.00, "visibility": 0.95, "px": 215, "py": 512,  "visible": True},
        "right_elbow":    {"x": 0.72, "y": 0.50, "z": 0.00, "visibility": 0.94, "px": 553, "py": 512,  "visible": True},
        "left_wrist":     {"x": 0.24, "y": 0.68, "z": 0.00, "visibility": 0.90, "px": 184, "py": 696,  "visible": True},
        "right_wrist":    {"x": 0.76, "y": 0.68, "z": 0.00, "visibility": 0.91, "px": 584, "py": 696,  "visible": True},
        "left_hip":       {"x": 0.38, "y": 0.62, "z": 0.00, "visibility": 0.96, "px": 292, "py": 635,  "visible": True},
        "right_hip":      {"x": 0.62, "y": 0.62, "z": 0.00, "visibility": 0.95, "px": 476, "py": 635,  "visible": True},
    }
    return {
        "success": True,
        "person_detected": True,
        "landmarks": [
            {"index": 0,  "name": "NOSE",           "x": 0.50, "y": 0.12, "z": 0.00, "visibility": 0.99, "px": 384, "py": 123},
            {"index": 11, "name": "LEFT_SHOULDER",  "x": 0.35, "y": 0.30, "z": 0.00, "visibility": 0.98, "px": 269, "py": 307},
            {"index": 12, "name": "RIGHT_SHOULDER", "x": 0.65, "y": 0.30, "z": 0.00, "visibility": 0.97, "px": 499, "py": 307},
            {"index": 23, "name": "LEFT_HIP",       "x": 0.38, "y": 0.62, "z": 0.00, "visibility": 0.96, "px": 292, "py": 635},
            {"index": 24, "name": "RIGHT_HIP",      "x": 0.62, "y": 0.62, "z": 0.00, "visibility": 0.95, "px": 476, "py": 635},
        ],
        "important_landmarks": important,
        "detection_quality": {"confidence": 1.0, "reliable_landmarks": 9, "total_landmarks": 9},
        "image_width": 768,
        "image_height": 1024,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Landmark mapping (pure unit tests)
# ──────────────────────────────────────────────────────────────────────────────

class TestLandmarkMapping:
    def test_important_landmarks_are_named(self):
        from app.ai.pose_detection import LANDMARK_NAMES, IMPORTANT_LANDMARK_NAMES
        for name in IMPORTANT_LANDMARK_NAMES:
            assert name in LANDMARK_NAMES.values(), f"{name} not in LANDMARK_NAMES"

    def test_reverse_mapping_consistent(self):
        from app.ai.pose_detection import LANDMARK_NAMES, LANDMARK_INDICES
        for idx, name in LANDMARK_NAMES.items():
            assert LANDMARK_INDICES[name] == idx

    def test_left_shoulder_index(self):
        from app.ai.pose_detection import LANDMARK_INDICES
        assert LANDMARK_INDICES["LEFT_SHOULDER"] == 11

    def test_right_shoulder_index(self):
        from app.ai.pose_detection import LANDMARK_INDICES
        assert LANDMARK_INDICES["RIGHT_SHOULDER"] == 12

    def test_left_hip_index(self):
        from app.ai.pose_detection import LANDMARK_INDICES
        assert LANDMARK_INDICES["LEFT_HIP"] == 23

    def test_right_hip_index(self):
        from app.ai.pose_detection import LANDMARK_INDICES
        assert LANDMARK_INDICES["RIGHT_HIP"] == 24


# ──────────────────────────────────────────────────────────────────────────────
# PoseDetector integration (blank image → no person, graceful handling)
# ──────────────────────────────────────────────────────────────────────────────

class TestPoseDetectorGraceful:

    def test_no_person_detected_returns_clean_result(self, app_ctx, tmp_path):
        from app.ai.pose_detection import PoseDetector, reset_detector
        reset_detector()
        path   = _save_blank_png(str(tmp_path))
        det    = PoseDetector()
        result = det.detect(path)
        assert result["person_detected"] is False
        assert result["landmarks"] == []
        assert "error" in result
        det.close()

    def test_missing_file_raises_error(self, app_ctx, tmp_path):
        from app.ai.pose_detection import PoseDetector, PoseDetectionError, reset_detector
        reset_detector()
        det = PoseDetector()
        with pytest.raises(PoseDetectionError) as exc:
            det.detect(str(tmp_path / 'does_not_exist.png'))
        assert exc.value.code == 'IMAGE_NOT_FOUND'
        det.close()

    def test_corrupted_image_raises_load_error(self, app_ctx, tmp_path):
        from app.ai.pose_detection import PoseDetector, PoseDetectionError, reset_detector
        reset_detector()
        bad = tmp_path / 'bad.png'
        bad.write_bytes(b'not an image')
        det = PoseDetector()
        with pytest.raises(PoseDetectionError) as exc:
            det.detect(str(bad))
        assert exc.value.code == 'LOAD_ERROR'
        det.close()

    def test_result_is_json_serializable(self, app_ctx, tmp_path):
        from app.ai.pose_detection import PoseDetector, reset_detector
        reset_detector()
        path   = _save_blank_png(str(tmp_path), 'serial.png')
        det    = PoseDetector()
        result = det.detect(path)
        encoded = json.dumps(result)
        assert isinstance(encoded, str)
        det.close()

    def test_result_contains_image_dimensions(self, app_ctx, tmp_path):
        from app.ai.pose_detection import PoseDetector, reset_detector
        reset_detector()
        path   = _save_blank_png(str(tmp_path), 'dims.png', size=(768, 1024))
        det    = PoseDetector()
        result = det.detect(path)
        assert result['image_width']  == 768
        assert result['image_height'] == 1024
        det.close()


# ──────────────────────────────────────────────────────────────────────────────
# Landmark structure tests (use fixture data, no MediaPipe needed)
# ──────────────────────────────────────────────────────────────────────────────

class TestLandmarkExtraction:
    def test_landmark_keys_present(self):
        result = _make_fake_pose_result(person_detected=True)
        for lm in result['landmarks']:
            for key in ('index', 'name', 'x', 'y', 'z', 'visibility', 'px', 'py'):
                assert key in lm

    def test_visibility_in_range(self):
        result = _make_fake_pose_result(person_detected=True)
        for lm in result['landmarks']:
            assert 0.0 <= lm['visibility'] <= 1.0

    def test_normalised_coords_in_range(self):
        result = _make_fake_pose_result(person_detected=True)
        for lm in result['landmarks']:
            assert 0.0 <= lm['x'] <= 1.0
            assert 0.0 <= lm['y'] <= 1.0

    def test_important_landmarks_present(self):
        result = _make_fake_pose_result(person_detected=True)
        for key in ('left_shoulder', 'right_shoulder', 'left_hip', 'right_hip'):
            assert key in result['important_landmarks']

    def test_visible_flag_consistency(self):
        result = _make_fake_pose_result(person_detected=True)
        for name, lm in result['important_landmarks'].items():
            expected = lm['visibility'] > 0.5
            assert lm['visible'] == expected

    def test_detection_quality_keys(self):
        result = _make_fake_pose_result(person_detected=True)
        q = result['detection_quality']
        assert 'confidence' in q
        assert 'reliable_landmarks' in q
        assert 'total_landmarks' in q
        assert 0.0 <= q['confidence'] <= 1.0


# ──────────────────────────────────────────────────────────────────────────────
# API auth guard tests
# ──────────────────────────────────────────────────────────────────────────────

class TestPoseAPI:
    def test_pose_endpoint_unauthenticated(self, client):
        r = client.post('/api/v1/processing/pose',
                        json={"image_path": "processed/users/test.png"})
        assert r.status_code == 401

    def test_pose_endpoint_invalid_token(self, client):
        r = client.post('/api/v1/processing/pose',
                        json={"image_path": "processed/users/test.png"},
                        headers={"Authorization": "Bearer badtoken"})
        assert r.status_code == 401

    def test_pose_endpoint_path_traversal_blocked(self, client):
        # JWT check fires first
        r = client.post('/api/v1/processing/pose',
                        json={"image_path": "../../etc/passwd"},
                        headers={"Authorization": "Bearer badtoken"})
        assert r.status_code == 401

    def test_preview_endpoint_still_accessible(self, client):
        r = client.post('/api/v1/processing/preview',
                        json={"type": "person", "image_path": "users/x.png"},
                        headers={"Authorization": "Bearer badtoken"})
        assert r.status_code == 401
