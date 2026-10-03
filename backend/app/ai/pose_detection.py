"""
app/ai/pose_detection.py

MediaPipe-based human pose detection using the MediaPipe Tasks API
(mediapipe >= 0.10.x).

Uses PoseLandmarker with a downloaded .task model file.

CURRENT STAGE: Detect body landmarks from a preprocessed person image.

NOT IMPLEMENTED HERE:
  - Background removal / segmentation
  - Garment masking / alignment
  - Virtual try-on inference

Public API
----------
    detector = PoseDetector()
    result   = detector.detect(image_path)

    # or the module-level convenience wrapper:
    result = detect_pose(image_path)
"""

import os
import math
import logging
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from flask import current_app

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Default model path (relative to this file's package root = backend/)
# ──────────────────────────────────────────────────────────────────────────────

_BACKEND_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DEFAULT_MODEL = os.path.join(_BACKEND_DIR, 'models', 'pose_landmarker_full.task')


# ──────────────────────────────────────────────────────────────────────────────
# Landmark name mapping  (MediaPipe Tasks PoseLandmark enum values)
# ──────────────────────────────────────────────────────────────────────────────

LANDMARK_NAMES = {
    0:  "NOSE",
    1:  "LEFT_EYE_INNER",
    2:  "LEFT_EYE",
    3:  "LEFT_EYE_OUTER",
    4:  "RIGHT_EYE_INNER",
    5:  "RIGHT_EYE",
    6:  "RIGHT_EYE_OUTER",
    7:  "LEFT_EAR",
    8:  "RIGHT_EAR",
    9:  "MOUTH_LEFT",
    10: "MOUTH_RIGHT",
    11: "LEFT_SHOULDER",
    12: "RIGHT_SHOULDER",
    13: "LEFT_ELBOW",
    14: "RIGHT_ELBOW",
    15: "LEFT_WRIST",
    16: "RIGHT_WRIST",
    17: "LEFT_PINKY",
    18: "RIGHT_PINKY",
    19: "LEFT_INDEX",
    20: "RIGHT_INDEX",
    21: "LEFT_THUMB",
    22: "RIGHT_THUMB",
    23: "LEFT_HIP",
    24: "RIGHT_HIP",
    25: "LEFT_KNEE",
    26: "RIGHT_KNEE",
    27: "LEFT_ANKLE",
    28: "RIGHT_ANKLE",
    29: "LEFT_HEEL",
    30: "RIGHT_HEEL",
    31: "LEFT_FOOT_INDEX",
    32: "RIGHT_FOOT_INDEX",
}

# Reverse mapping: name → index
LANDMARK_INDICES = {v: k for k, v in LANDMARK_NAMES.items()}

# Upper-body landmarks the try-on pipeline specifically needs
IMPORTANT_LANDMARK_NAMES = [
    "NOSE",
    "LEFT_SHOULDER",
    "RIGHT_SHOULDER",
    "LEFT_ELBOW",
    "RIGHT_ELBOW",
    "LEFT_WRIST",
    "RIGHT_WRIST",
    "LEFT_HIP",
    "RIGHT_HIP",
]


# ──────────────────────────────────────────────────────────────────────────────
# Exceptions
# ──────────────────────────────────────────────────────────────────────────────

class PoseDetectionError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code    = code
        super().__init__(message)


# ──────────────────────────────────────────────────────────────────────────────
# PoseDetector
# ──────────────────────────────────────────────────────────────────────────────

class PoseDetector:
    """
    Wraps MediaPipe PoseLandmarker (Tasks API) for static image inference.

    One instance can be reused across multiple detect() calls.
    Initialise once; call detect() per image.
    """

    def __init__(
        self,
        model_path: str | None = None,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence:  float = 0.5,
    ):
        # Prefer explicit argument, then Flask config, then default path
        if model_path is None:
            model_path = _get_config_str("POSE_MODEL_PATH", _DEFAULT_MODEL)

        if not os.path.isfile(model_path):
            raise PoseDetectionError(
                f"Pose landmarker model not found at: {model_path}. "
                "Run the model download command in README.",
                "MODEL_NOT_FOUND"
            )

        base_opts = mp_python.BaseOptions(model_asset_path=model_path)
        options   = mp_vision.PoseLandmarkerOptions(
            base_options=base_opts,
            running_mode=mp_vision.RunningMode.IMAGE,
            min_pose_detection_confidence=min_detection_confidence,
            min_pose_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence,
            num_poses=1,            # single-person workflow
            output_segmentation_masks=False,  # not needed at this stage
        )

        self._landmarker = mp_vision.PoseLandmarker.create_from_options(options)
        logger.debug(
            "PoseDetector initialised (det=%.2f, trk=%.2f, model=%s)",
            min_detection_confidence, min_tracking_confidence, model_path,
        )

    # ── Core detection ────────────────────────────────────────────────────────

    def detect(self, image_path: str) -> dict:
        """
        Run pose detection on a preprocessed person image.

        Parameters
        ----------
        image_path : str
            Absolute path to the person image (should be the preprocessed
            version produced by the preprocessing pipeline).

        Returns
        -------
        dict  – structured pose result.
        """
        if not os.path.isfile(image_path):
            raise PoseDetectionError("Image file not found", "IMAGE_NOT_FOUND")

        # Load with OpenCV and verify
        bgr = cv2.imread(image_path)
        if bgr is None:
            raise PoseDetectionError("Failed to load image", "LOAD_ERROR")

        h, w = bgr.shape[:2]

        # MediaPipe Tasks API expects mp.Image with RGB pixel data
        rgb       = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        mp_image  = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        try:
            detection_result = self._landmarker.detect(mp_image)
        except Exception as exc:
            logger.error("MediaPipe PoseLandmarker failed: %s", exc)
            raise PoseDetectionError("Pose processing failed", "MEDIAPIPE_ERROR")

        # detection_result.pose_landmarks is a list of lists (one per person)
        if not detection_result.pose_landmarks:
            return {
                "success":             False,
                "person_detected":     False,
                "landmarks":           [],
                "important_landmarks": {},
                "image_width":         w,
                "image_height":        h,
                "error":               "No person detected in the image",
            }

        # Take the first (and typically only) detected person
        raw_landmarks = detection_result.pose_landmarks[0]

        landmarks = self._extract_landmarks(raw_landmarks, w, h)
        important = self._extract_important(landmarks)
        min_vis   = _get_config_float("POSE_MIN_VISIBILITY", 0.5)
        quality   = self._evaluate_quality(important, min_vis)

        return {
            "success":             True,
            "person_detected":     True,
            "landmarks":           landmarks,
            "important_landmarks": important,
            "detection_quality":   quality,
            "image_width":         w,
            "image_height":        h,
        }

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _extract_landmarks(raw_landmarks, img_w: int, img_h: int) -> list:
        """
        Convert MediaPipe NormalizedLandmark list to a list of JSON-safe dicts.

        Coordinates are kept normalised (0.0–1.0).
        Pixel coordinates are also included for convenience.
        """
        result = []
        for idx, lm in enumerate(raw_landmarks):
            result.append({
                "index":      idx,
                "name":       LANDMARK_NAMES.get(idx, f"LANDMARK_{idx}"),
                "x":          round(float(lm.x),          6),
                "y":          round(float(lm.y),          6),
                "z":          round(float(lm.z),          6),
                "visibility": round(float(lm.visibility), 6),
                "px":         round(float(lm.x) * img_w),
                "py":         round(float(lm.y) * img_h),
            })
        return result

    @staticmethod
    def _extract_important(landmarks: list) -> dict:
        """Build a name-keyed dict for the upper-body try-on landmarks."""
        by_name   = {lm["name"]: lm for lm in landmarks}
        important = {}
        for name in IMPORTANT_LANDMARK_NAMES:
            lm = by_name.get(name)
            if lm:
                important[name.lower()] = {
                    "x":          lm["x"],
                    "y":          lm["y"],
                    "z":          lm["z"],
                    "visibility": lm["visibility"],
                    "px":         lm["px"],
                    "py":         lm["py"],
                    "visible":    lm["visibility"] > 0.5,
                }
        return important

    @staticmethod
    def _evaluate_quality(important: dict, min_visibility: float) -> dict:
        """Fraction of important landmarks that exceed the visibility threshold."""
        if not important:
            return {"confidence": 0.0, "reliable_landmarks": 0, "total_landmarks": 0}

        reliable = sum(
            1 for lm in important.values()
            if lm.get("visibility", 0) >= min_visibility
        )
        total = len(important)
        return {
            "confidence":         round(reliable / total, 4),
            "reliable_landmarks": reliable,
            "total_landmarks":    total,
        }

    def close(self):
        """Release the underlying MediaPipe resources."""
        try:
            self._landmarker.close()
        except Exception:
            pass

    def __del__(self):
        self.close()


# ──────────────────────────────────────────────────────────────────────────────
# Module-level singleton + convenience wrapper
# ──────────────────────────────────────────────────────────────────────────────

_detector: PoseDetector | None = None


def get_detector() -> PoseDetector:
    """Return (and lazily create) the module-level PoseDetector singleton."""
    global _detector
    if _detector is None:
        det_conf   = _get_config_float("POSE_MIN_DETECTION_CONFIDENCE", 0.5)
        trk_conf   = _get_config_float("POSE_MIN_TRACKING_CONFIDENCE",  0.5)
        model_path = _get_config_str("POSE_MODEL_PATH", _DEFAULT_MODEL)
        _detector  = PoseDetector(
            model_path=model_path,
            min_detection_confidence=det_conf,
            min_tracking_confidence=trk_conf,
        )
    return _detector


def detect_pose(image_path: str) -> dict:
    """Convenience wrapper using the module-level singleton detector."""
    return get_detector().detect(image_path)


def reset_detector():
    """Force singleton recreation on next use (useful in tests)."""
    global _detector
    if _detector is not None:
        _detector.close()
    _detector = None


# ──────────────────────────────────────────────────────────────────────────────
# Config helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_config_float(key: str, default: float) -> float:
    try:
        return float(current_app.config.get(key, default))
    except RuntimeError:
        return default


def _get_config_str(key: str, default: str) -> str:
    try:
        val = current_app.config.get(key, default)
        return val if val else default
    except RuntimeError:
        return default
