"""
tests/test_body_analysis.py

Unit tests for the geometric body analysis functions in app/ai/body_analysis.py.

All tests here are PURE UNIT TESTS – no Flask app context, no MediaPipe,
no file I/O.  They use synthetic landmark dicts that mirror the structure
produced by PoseDetector._extract_important().
"""

import math
import pytest


# ──────────────────────────────────────────────────────────────────────────────
# Shared fixtures
# ──────────────────────────────────────────────────────────────────────────────

def _lm(x: float, y: float, vis: float = 0.99) -> dict:
    """Build a minimal landmark dict."""
    return {"x": x, "y": y, "z": 0.0, "visibility": vis,
            "px": round(x * 768), "py": round(y * 1024), "visible": vis > 0.5}


def _full_pose_result(person_detected=True) -> dict:
    """Return a synthetic pose result with all required landmarks."""
    if not person_detected:
        return {"person_detected": False, "landmarks": [], "important_landmarks": {}}

    return {
        "person_detected": True,
        "landmarks": [],
        "important_landmarks": {
            "nose":           _lm(0.50, 0.12),
            "left_shoulder":  _lm(0.35, 0.30),
            "right_shoulder": _lm(0.65, 0.30),
            "left_elbow":     _lm(0.28, 0.50),
            "right_elbow":    _lm(0.72, 0.50),
            "left_wrist":     _lm(0.24, 0.68),
            "right_wrist":    _lm(0.76, 0.68),
            "left_hip":       _lm(0.38, 0.62),
            "right_hip":      _lm(0.62, 0.62),
        },
        "detection_quality": {"confidence": 1.0},
        "image_width": 768,
        "image_height": 1024,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Geometric helpers
# ──────────────────────────────────────────────────────────────────────────────

class TestGeometricHelpers:

    def test_distance_zero(self):
        from app.ai.body_analysis import distance_between_points
        p = _lm(0.5, 0.5)
        assert distance_between_points(p, p) == pytest.approx(0.0)

    def test_distance_horizontal(self):
        from app.ai.body_analysis import distance_between_points
        p1 = _lm(0.0, 0.5)
        p2 = _lm(0.3, 0.5)
        assert distance_between_points(p1, p2) == pytest.approx(0.3, abs=1e-6)

    def test_distance_vertical(self):
        from app.ai.body_analysis import distance_between_points
        p1 = _lm(0.5, 0.0)
        p2 = _lm(0.5, 0.4)
        assert distance_between_points(p1, p2) == pytest.approx(0.4, abs=1e-6)

    def test_distance_diagonal(self):
        from app.ai.body_analysis import distance_between_points
        p1 = _lm(0.0, 0.0)
        p2 = _lm(0.3, 0.4)
        # 3-4-5 right triangle scaled by 0.1
        assert distance_between_points(p1, p2) == pytest.approx(0.5, abs=1e-6)

    def test_midpoint_centre(self):
        from app.ai.body_analysis import midpoint
        p1 = _lm(0.2, 0.4)
        p2 = _lm(0.8, 0.6)
        m  = midpoint(p1, p2)
        assert m["x"] == pytest.approx(0.5, abs=1e-6)
        assert m["y"] == pytest.approx(0.5, abs=1e-6)

    def test_midpoint_same_point(self):
        from app.ai.body_analysis import midpoint
        p  = _lm(0.3, 0.7)
        m  = midpoint(p, p)
        assert m["x"] == pytest.approx(0.3, abs=1e-6)
        assert m["y"] == pytest.approx(0.7, abs=1e-6)

    def test_angle_horizontal_zero(self):
        from app.ai.body_analysis import angle_between_points
        left  = _lm(0.3, 0.5)
        right = _lm(0.7, 0.5)
        angle = angle_between_points(left, right)
        assert angle == pytest.approx(0.0, abs=1e-4)

    def test_angle_45_degrees(self):
        from app.ai.body_analysis import angle_between_points
        left  = _lm(0.0, 0.0)
        right = _lm(0.1, 0.1)
        angle = angle_between_points(left, right)
        assert angle == pytest.approx(45.0, abs=0.01)

    def test_upper_body_region_contains_all_points(self):
        from app.ai.body_analysis import calculate_upper_body_region
        ls = _lm(0.35, 0.30)
        rs = _lm(0.65, 0.30)
        lh = _lm(0.38, 0.62)
        rh = _lm(0.62, 0.62)
        region = calculate_upper_body_region(ls, rs, lh, rh, padding=0.0)
        assert region["x_min"] <= 0.35
        assert region["x_max"] >= 0.65
        assert region["y_min"] <= 0.30
        assert region["y_max"] >= 0.62

    def test_upper_body_region_clamped_to_01(self):
        from app.ai.body_analysis import calculate_upper_body_region
        ls = _lm(0.02, 0.02)
        rs = _lm(0.98, 0.02)
        lh = _lm(0.02, 0.98)
        rh = _lm(0.98, 0.98)
        region = calculate_upper_body_region(ls, rs, lh, rh, padding=0.10)
        assert region["x_min"] >= 0.0
        assert region["x_max"] <= 1.0
        assert region["y_min"] >= 0.0
        assert region["y_max"] <= 1.0

    def test_upper_body_region_padding_expands_box(self):
        from app.ai.body_analysis import calculate_upper_body_region
        ls = _lm(0.35, 0.30)
        rs = _lm(0.65, 0.30)
        lh = _lm(0.35, 0.62)
        rh = _lm(0.65, 0.62)
        no_pad = calculate_upper_body_region(ls, rs, lh, rh, padding=0.0)
        padded = calculate_upper_body_region(ls, rs, lh, rh, padding=0.05)
        assert padded["x_min"] < no_pad["x_min"]
        assert padded["x_max"] > no_pad["x_max"]
        assert padded["y_min"] < no_pad["y_min"]
        assert padded["y_max"] > no_pad["y_max"]


# ──────────────────────────────────────────────────────────────────────────────
# analyse_body integration tests (synthetic pose result)
# ──────────────────────────────────────────────────────────────────────────────

class TestAnalyseBody:

    def test_analyse_body_success(self):
        from app.ai.body_analysis import analyse_body
        result = analyse_body(_full_pose_result())
        assert "shoulder_width"    in result
        assert "hip_width"         in result
        assert "shoulder_center"   in result
        assert "hip_center"        in result
        assert "body_center"       in result
        assert "shoulder_angle"    in result
        assert "upper_body_region" in result
        assert "torso_height"      in result
        assert "pose_suitable_for_tryon" in result

    def test_shoulder_width_correct(self):
        from app.ai.body_analysis import analyse_body, distance_between_points
        pose   = _full_pose_result()
        result = analyse_body(pose)
        ls = pose["important_landmarks"]["left_shoulder"]
        rs = pose["important_landmarks"]["right_shoulder"]
        expected = distance_between_points(ls, rs)
        assert result["shoulder_width"] == pytest.approx(expected, abs=1e-5)

    def test_hip_width_correct(self):
        from app.ai.body_analysis import analyse_body, distance_between_points
        pose   = _full_pose_result()
        result = analyse_body(pose)
        lh = pose["important_landmarks"]["left_hip"]
        rh = pose["important_landmarks"]["right_hip"]
        expected = distance_between_points(lh, rh)
        assert result["hip_width"] == pytest.approx(expected, abs=1e-5)

    def test_shoulder_center_correct(self):
        from app.ai.body_analysis import analyse_body
        pose   = _full_pose_result()
        result = analyse_body(pose)
        # Left 0.35, right 0.65 → center 0.50
        assert result["shoulder_center"]["x"] == pytest.approx(0.50, abs=1e-5)
        assert result["shoulder_center"]["y"] == pytest.approx(0.30, abs=1e-5)

    def test_hip_center_correct(self):
        from app.ai.body_analysis import analyse_body
        pose   = _full_pose_result()
        result = analyse_body(pose)
        assert result["hip_center"]["x"] == pytest.approx(0.50, abs=1e-5)
        assert result["hip_center"]["y"] == pytest.approx(0.62, abs=1e-5)

    def test_shoulder_angle_near_zero_for_level_shoulders(self):
        from app.ai.body_analysis import analyse_body
        pose   = _full_pose_result()
        result = analyse_body(pose)
        # Both shoulders at y=0.30 → angle = 0
        assert result["shoulder_angle"] == pytest.approx(0.0, abs=0.01)

    def test_tilted_shoulders_nonzero_angle(self):
        from app.ai.body_analysis import analyse_body
        pose = _full_pose_result()
        # Tilt right shoulder lower
        pose["important_landmarks"]["right_shoulder"]["y"] = 0.40
        result = analyse_body(pose)
        assert result["shoulder_angle"] != pytest.approx(0.0, abs=0.01)

    def test_pose_suitable_when_level(self):
        from app.ai.body_analysis import analyse_body
        result = analyse_body(_full_pose_result())
        assert result["pose_suitable_for_tryon"] is True

    def test_pose_not_suitable_when_extreme_tilt(self):
        from app.ai.body_analysis import analyse_body
        pose = _full_pose_result()
        # Extreme tilt: right shoulder much lower than left
        pose["important_landmarks"]["right_shoulder"]["y"] = 0.70
        result = analyse_body(pose)
        assert result["pose_suitable_for_tryon"] is False

    def test_upper_body_region_present(self):
        from app.ai.body_analysis import analyse_body
        result = analyse_body(_full_pose_result())
        region = result["upper_body_region"]
        for key in ("x_min", "y_min", "x_max", "y_max"):
            assert key in region
            assert 0.0 <= region[key] <= 1.0

    def test_elbow_span_when_elbows_present(self):
        from app.ai.body_analysis import analyse_body
        result = analyse_body(_full_pose_result())
        assert "elbow_span" in result
        assert result["elbow_span"] > 0.0

    def test_no_person_raises_error(self):
        from app.ai.body_analysis import analyse_body, BodyAnalysisError
        with pytest.raises(BodyAnalysisError) as exc:
            analyse_body(_full_pose_result(person_detected=False))
        assert exc.value.code == "NO_PERSON_DETECTED"

    def test_missing_shoulder_raises_error(self):
        from app.ai.body_analysis import analyse_body, BodyAnalysisError
        pose = _full_pose_result()
        del pose["important_landmarks"]["left_shoulder"]
        with pytest.raises(BodyAnalysisError) as exc:
            analyse_body(pose)
        assert exc.value.code == "MISSING_LANDMARKS"

    def test_missing_hip_raises_error(self):
        from app.ai.body_analysis import analyse_body, BodyAnalysisError
        pose = _full_pose_result()
        del pose["important_landmarks"]["right_hip"]
        with pytest.raises(BodyAnalysisError) as exc:
            analyse_body(pose)
        assert exc.value.code == "MISSING_LANDMARKS"

    def test_result_is_json_serializable(self):
        import json
        from app.ai.body_analysis import analyse_body
        result = analyse_body(_full_pose_result())
        encoded = json.dumps(result)
        assert isinstance(encoded, str)

    def test_torso_height_positive(self):
        from app.ai.body_analysis import analyse_body
        result = analyse_body(_full_pose_result())
        # shoulder y=0.30, hip y=0.62 → torso_height = 0.32
        assert result["torso_height"] == pytest.approx(0.32, abs=1e-5)
