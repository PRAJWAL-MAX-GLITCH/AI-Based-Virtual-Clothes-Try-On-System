"""
app/ai/body_analysis.py

Basic geometric body analysis from MediaPipe pose landmarks.

Consumes the structured pose result produced by pose_detection.py.
Does NOT re-run MediaPipe.

CURRENT STAGE: Pure geometry – distances, midpoints, bounding regions,
               and shoulder angle from normalised landmark coordinates.

NOT IMPLEMENTED HERE:
  - Body measurement prediction
  - Segmentation / masking
  - Garment alignment
  - Virtual try-on

Public API
----------
    from app.ai.body_analysis import analyse_body

    pose_result  = detect_pose(image_path)       # from pose_detection.py
    body_info    = analyse_body(pose_result)
"""

import math
import logging

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Exceptions
# ──────────────────────────────────────────────────────────────────────────────

class BodyAnalysisError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code    = code
        super().__init__(message)


# ──────────────────────────────────────────────────────────────────────────────
# Pure geometric helpers
# ──────────────────────────────────────────────────────────────────────────────

def distance_between_points(p1: dict, p2: dict) -> float:
    """
    Euclidean distance between two landmark dicts using normalised (x, y).
    Result is also normalised (0.0–1.0 range along each axis).
    """
    dx = p1["x"] - p2["x"]
    dy = p1["y"] - p2["y"]
    return math.sqrt(dx * dx + dy * dy)


def midpoint(p1: dict, p2: dict) -> dict:
    """Return the midpoint of two landmark dicts (normalised x, y)."""
    return {
        "x": round((p1["x"] + p2["x"]) / 2, 6),
        "y": round((p1["y"] + p2["y"]) / 2, 6),
    }


def angle_between_points(p_left: dict, p_right: dict) -> float:
    """
    Calculate the angle (in degrees) of the line from p_left to p_right
    relative to the horizontal axis.

    Positive angles indicate the right point is below the left.
    Used to estimate torso/shoulder tilt.
    """
    dx = p_right["x"] - p_left["x"]
    dy = p_right["y"] - p_left["y"]
    return round(math.degrees(math.atan2(dy, dx)), 4)


def calculate_upper_body_region(
    left_shoulder:  dict,
    right_shoulder: dict,
    left_hip:       dict,
    right_hip:      dict,
    padding: float = 0.05,
) -> dict:
    """
    Compute a rough bounding box for the upper body region using four
    landmark points (normalised coordinates).

    A small padding factor is added on each side so future garment
    placement has a margin.

    Returns
    -------
    dict  { x_min, y_min, x_max, y_max }  – all normalised 0.0–1.0
    """
    xs = [left_shoulder["x"], right_shoulder["x"], left_hip["x"], right_hip["x"]]
    ys = [left_shoulder["y"], right_shoulder["y"], left_hip["y"], right_hip["y"]]

    x_min = max(0.0, min(xs) - padding)
    x_max = min(1.0, max(xs) + padding)
    y_min = max(0.0, min(ys) - padding)
    y_max = min(1.0, max(ys) + padding)

    return {
        "x_min": round(x_min, 6),
        "y_min": round(y_min, 6),
        "x_max": round(x_max, 6),
        "y_max": round(y_max, 6),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Main analysis function
# ──────────────────────────────────────────────────────────────────────────────

def analyse_body(pose_result: dict) -> dict:
    """
    Perform geometric body analysis on a pose detection result.

    Parameters
    ----------
    pose_result : dict
        The dict returned by PoseDetector.detect() or detect_pose().

    Returns
    -------
    dict  – body analysis result (see module docstring for schema).

    Raises
    ------
    BodyAnalysisError  – if no person was detected or essential landmarks
                         are missing.
    """
    if not pose_result.get("person_detected"):
        raise BodyAnalysisError("No person detected in the image", "NO_PERSON_DETECTED")

    lm = pose_result.get("important_landmarks", {})

    # ── Require the four core upper-body landmarks ────────────────────────────
    required = ["left_shoulder", "right_shoulder", "left_hip", "right_hip"]
    missing  = [k for k in required if k not in lm]
    if missing:
        raise BodyAnalysisError(
            f"Missing essential landmarks: {', '.join(missing)}",
            "MISSING_LANDMARKS",
        )

    ls = lm["left_shoulder"]
    rs = lm["right_shoulder"]
    lh = lm["left_hip"]
    rh = lm["right_hip"]

    # ── Core measurements ─────────────────────────────────────────────────────
    shoulder_width  = round(distance_between_points(ls, rs), 6)
    hip_width       = round(distance_between_points(lh, rh), 6)
    shoulder_center = midpoint(ls, rs)
    hip_center      = midpoint(lh, rh)

    # Torso height = vertical distance between shoulder center and hip center
    torso_height    = round(abs(shoulder_center["y"] - hip_center["y"]), 6)

    # Overall body center (midpoint of shoulder_center and hip_center)
    body_center = midpoint(shoulder_center, hip_center)

    # ── Shoulder angle ────────────────────────────────────────────────────────
    # Positive → right shoulder lower than left; Negative → left shoulder lower
    # Near 0° → person is facing camera (good for try-on)
    shoulder_angle  = angle_between_points(ls, rs)

    # ── Upper body bounding region ────────────────────────────────────────────
    upper_body_region = calculate_upper_body_region(ls, rs, lh, rh)

    # ── Elbow / wrist data (optional, present when visible) ───────────────────
    elbow_span = None
    le = lm.get("left_elbow")
    re = lm.get("right_elbow")
    if le and re:
        elbow_span = round(distance_between_points(le, re), 6)

    # ── Quality notes ─────────────────────────────────────────────────────────
    # Warn if shoulder angle is very large (person may be sideways)
    pose_suitable = abs(shoulder_angle) < 30.0

    result = {
        "shoulder_width":     shoulder_width,
        "hip_width":          hip_width,
        "torso_height":       torso_height,
        "shoulder_center":    shoulder_center,
        "hip_center":         hip_center,
        "body_center":        body_center,
        "shoulder_angle":     shoulder_angle,
        "upper_body_region":  upper_body_region,
        "pose_suitable_for_tryon": pose_suitable,
    }

    if elbow_span is not None:
        result["elbow_span"] = elbow_span

    return result
