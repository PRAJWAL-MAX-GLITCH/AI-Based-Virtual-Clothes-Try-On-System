"""
app/ai/preprocessing.py

Image preprocessing pipeline for the AI-Based Virtual Clothes Try-On System.

CURRENT STAGE: Standardise uploaded images into a consistent format
               ready for future AI processing (pose detection, garment
               alignment, virtual try-on).

NOT IMPLEMENTED HERE:
  - MediaPipe / pose detection
  - Background removal / segmentation
  - Garment masking / alignment
  - Virtual try-on inference

Usage
-----
    from app.ai.preprocessing import preprocess_person_image, preprocess_clothing_image

Both functions return a PreprocessingResult dict.
"""

import os
import logging
from flask import current_app
from app.utils.image_utils import (
    validate_image_file,
    to_rgb,
    to_rgba,
    resize_and_pad,
    generate_processed_filename,
    save_image,
    ImageUtilsError,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Exceptions
# ──────────────────────────────────────────────────────────────────────────────

class PreprocessingError(Exception):
    """Raised when the preprocessing pipeline cannot complete."""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_processed_dir(sub: str) -> str:
    """
    Return the absolute path to uploads/processed/<sub>/ and create it if
    it does not exist.

    sub is one of: 'users', 'clothing'
    """
    base = current_app.config['UPLOAD_FOLDER']
    directory = os.path.join(base, 'processed', sub)
    os.makedirs(directory, exist_ok=True)
    return directory


def _config_target() -> tuple:
    """Return (target_width, target_height) from app config."""
    w = current_app.config.get('PREPROCESS_TARGET_WIDTH', 768)
    h = current_app.config.get('PREPROCESS_TARGET_HEIGHT', 1024)
    return int(w), int(h)


def _config_min_dims() -> tuple:
    """Return (min_width, min_height) from app config."""
    w = current_app.config.get('PREPROCESS_MIN_WIDTH', 64)
    h = current_app.config.get('PREPROCESS_MIN_HEIGHT', 64)
    return int(w), int(h)


def _config_pad_color() -> tuple:
    """Return the RGB pad colour from app config."""
    return current_app.config.get('PREPROCESS_PAD_COLOR', (255, 255, 255))


def _resolve_absolute(relative_or_absolute_path: str) -> str:
    """
    Given a path that may be relative (stored in MongoDB, e.g.
    'users/abc.png') or absolute, return the full absolute path
    inside the UPLOAD_FOLDER.

    Never trusts caller-supplied absolute paths that escape the upload root.
    """
    upload_root = current_app.config['UPLOAD_FOLDER']

    if os.path.isabs(relative_or_absolute_path):
        # Verify it is still inside the upload root
        if not os.path.abspath(relative_or_absolute_path).startswith(
            os.path.abspath(upload_root)
        ):
            raise PreprocessingError("Invalid image path", "INVALID_PATH")
        return relative_or_absolute_path

    # Relative path  →  join with upload root
    normalized = os.path.normpath(relative_or_absolute_path)
    if normalized.startswith('..'):
        raise PreprocessingError("Invalid image path", "INVALID_PATH")

    return os.path.join(upload_root, normalized)


def _build_result(
    original_path: str,
    processed_path: str,
    resize_meta: dict,
    image_type: str,
) -> dict:
    """Construct the standard PreprocessingResult dict."""
    upload_root = current_app.config['UPLOAD_FOLDER']

    def _relative(p):
        try:
            return os.path.relpath(p, upload_root).replace('\\', '/')
        except ValueError:
            return p

    return {
        "type":              image_type,
        "original_path":     _relative(original_path),
        "processed_path":    _relative(processed_path),
        "original_size": {
            "width":  resize_meta["original_width"],
            "height": resize_meta["original_height"],
        },
        "processed_size": {
            "width":  current_app.config.get('PREPROCESS_TARGET_WIDTH', 768),
            "height": current_app.config.get('PREPROCESS_TARGET_HEIGHT', 1024),
        },
        "format":  "PNG",
        "mode":    "RGB",
        "scale":   resize_meta["scale"],
        "padding": resize_meta["padding"],
    }


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def preprocess_person_image(stored_relative_path: str) -> dict:
    """
    Preprocess a user / person image for the try-on pipeline.

    Steps
    -----
    1. Resolve absolute path (path-traversal safe)
    2. Validate the image (exists, decodable, min dimensions)
    3. Convert to RGB  (composites RGBA onto white background)
    4. Resize + pad to the configured target canvas
    5. Save to uploads/processed/users/  (original is NOT touched)
    6. Return PreprocessingResult metadata dict

    Not implemented here: pose detection, body landmark extraction,
    background removal, segmentation.
    """
    abs_path = _resolve_absolute(stored_relative_path)
    min_w, min_h = _config_min_dims()

    try:
        img = validate_image_file(abs_path, min_width=min_w, min_height=min_h)
    except ImageUtilsError as exc:
        raise PreprocessingError(exc.message, exc.code)

    # Normalise to RGB (white background for any alpha)
    img_rgb = to_rgb(img)

    target_w, target_h = _config_target()
    pad_color = _config_pad_color()

    canvas, meta = resize_and_pad(img_rgb, target_w, target_h, pad_color=pad_color)

    processed_dir = _get_processed_dir('users')
    filename      = generate_processed_filename('png')

    try:
        processed_abs = save_image(canvas, processed_dir, filename)
    except Exception as exc:
        logger.error("Failed to save processed person image: %s", exc)
        raise PreprocessingError("Failed to save processed image", "SAVE_ERROR")

    logger.info("Person image preprocessed: %s → %s", stored_relative_path, processed_abs)
    return _build_result(abs_path, processed_abs, meta, "person")


def preprocess_clothing_image(stored_relative_path: str, preserve_alpha: bool = False) -> dict:
    """
    Preprocess an admin catalog or user custom clothing image.

    The same function handles both clothing sources – the caller simply
    provides the stored relative path.

    Steps
    -----
    1. Resolve absolute path (path-traversal safe)
    2. Validate the image
    3. Handle transparency:
         preserve_alpha=False  →  composite onto white (RGB)
         preserve_alpha=True   →  keep RGBA  (for future garment masks)
    4. Resize + pad to the configured target canvas
    5. Save to uploads/processed/clothing/  (original is NOT touched)
    6. Return PreprocessingResult metadata dict

    Not implemented here: background removal, garment masking, alignment.
    """
    abs_path = _resolve_absolute(stored_relative_path)
    min_w, min_h = _config_min_dims()

    try:
        img = validate_image_file(abs_path, min_width=min_w, min_height=min_h)
    except ImageUtilsError as exc:
        raise PreprocessingError(exc.message, exc.code)

    if preserve_alpha:
        img_proc = to_rgba(img)
        mode_label = "RGBA"
    else:
        img_proc = to_rgb(img)
        mode_label = "RGB"

    target_w, target_h = _config_target()
    pad_color = _config_pad_color()

    canvas, meta = resize_and_pad(img_proc, target_w, target_h, pad_color=pad_color)

    processed_dir = _get_processed_dir('clothing')
    filename      = generate_processed_filename('png')

    try:
        processed_abs = save_image(canvas, processed_dir, filename)
    except Exception as exc:
        logger.error("Failed to save processed clothing image: %s", exc)
        raise PreprocessingError("Failed to save processed image", "SAVE_ERROR")

    result = _build_result(abs_path, processed_abs, meta, "clothing")
    result["mode"] = mode_label          # override if RGBA was kept
    logger.info("Clothing image preprocessed: %s → %s", stored_relative_path, processed_abs)
    return result
