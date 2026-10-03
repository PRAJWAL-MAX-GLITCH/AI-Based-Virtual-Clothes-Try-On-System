"""
app/ai/garment_processing.py

Basic geometric and image-level analysis for clothing images.
Works on both Admin Catalog and User Custom Clothing.

CURRENT STAGE: Garment analysis (dimensions, content bounding box).

NOT IMPLEMENTED HERE:
  - Advanced semantic segmentation / AI masks
  - Garment alignment / warping
  - Virtual try-on inference
"""

import os
import logging
import numpy as np
from PIL import Image
from flask import current_app

from app.utils.image_utils import validate_image_file, ImageUtilsError
from app.ai.preprocessing import preprocess_clothing_image, PreprocessingError

logger = logging.getLogger(__name__)


class GarmentProcessingError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code    = code
        super().__init__(message)


def _find_content_bounding_box(image_path: str, pad_color: tuple = (255, 255, 255), threshold: int = 15) -> dict:
    """
    Determine the approximate non-background region of the image.
    Uses the alpha channel if present, otherwise uses a difference threshold
    against the padding colour (default white).

    Returns a dict with normalised coordinates (0.0 to 1.0).
    Falls back to the full image if no distinct content is found.
    """
    try:
        img = Image.open(image_path)
    except Exception as exc:
        raise GarmentProcessingError(f"Failed to open image for analysis: {exc}", "IMAGE_READ_ERROR")

    w, h = img.size
    if w == 0 or h == 0:
        raise GarmentProcessingError("Image has zero width or height", "INVALID_DIMENSIONS")

    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        img_rgba = img.convert('RGBA')
        arr = np.array(img_rgba)
        alpha = arr[:, :, 3]
        mask = alpha > threshold
    else:
        img_rgb = img.convert('RGB')
        arr = np.array(img_rgb)
        diff = np.abs(arr.astype(int) - np.array(pad_color))
        max_diff = np.max(diff, axis=2)
        mask = max_diff > threshold

    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)

    if not np.any(rows) or not np.any(cols):
        # Empty or completely uniform background; fallback to full image
        return {
            "x_min": 0.0, "y_min": 0.0,
            "x_max": 1.0, "y_max": 1.0
        }

    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]

    # Ensure max is strictly greater than min to avoid 0-width regions
    if x_max == x_min: x_max = min(w - 1, x_min + 1)
    if y_max == y_min: y_max = min(h - 1, y_min + 1)

    return {
        "x_min": round(float(x_min) / w, 6),
        "y_min": round(float(y_min) / h, 6),
        "x_max": round(float(x_max) / w, 6),
        "y_max": round(float(y_max) / h, 6),
    }


def process_garment(clothing_id: str, stored_relative_path: str, source_type: str, category: str) -> dict:
    """
    Process a garment image for the virtual try-on pipeline.

    Steps:
    1. Resolve the processed clothing image (by running preprocessing if needed,
       which normalises size and handles basic formatting without destroying original).
    2. Extract basic image properties (format, mode, dimensions).
    3. Calculate the content bounding box (non-background region).
    4. Compute garment geometry (center, width, height) in pixels.

    Parameters:
    -----------
    clothing_id : str
        The database ID of the clothing record.
    stored_relative_path : str
        The relative path to the original uploaded image (e.g., 'clothing/catalog/shirt.png').
    source_type : str
        'catalog' or 'user_custom'
    category : str
        The garment category (e.g., 'shirt', 'dress').

    Returns:
    --------
    dict - Structured garment processing result.
    """
    if source_type not in ('catalog', 'user_custom'):
        raise GarmentProcessingError("Invalid source_type. Must be 'catalog' or 'user_custom'.", "INVALID_SOURCE")

    # 1. Ensure the image is preprocessed.
    # The preprocessing pipeline handles resolving the absolute path, path-traversal safety,
    # converting to the target canvas size, and saving to the processed/ directory.
    # We keep preserve_alpha=True so transparency is preserved for masking and alignment.
    try:
        prep_result = preprocess_clothing_image(stored_relative_path, preserve_alpha=True)
    except PreprocessingError as exc:
        raise GarmentProcessingError(exc.message, exc.code)

    upload_root = current_app.config['UPLOAD_FOLDER']
    processed_abs_path = os.path.join(upload_root, os.path.normpath(prep_result["processed_path"]))

    # 2. Extract image properties
    try:
        img = Image.open(processed_abs_path)
        img_format = img.format or "UNKNOWN"
        img_mode = img.mode
        w, h = img.size
    except Exception as exc:
        logger.error("Failed to read processed garment image properties: %s", exc)
        raise GarmentProcessingError("Failed to read processed image", "IMAGE_READ_ERROR")

    if w == 0 or h == 0:
        raise GarmentProcessingError("Processed image has zero width or height", "INVALID_DIMENSIONS")

    aspect_ratio = round(float(w) / float(h), 4)

    # 3. Calculate bounding box (normalised coords)
    pad_color = current_app.config.get('PREPROCESS_PAD_COLOR', (255, 255, 255))
    bbox_norm = _find_content_bounding_box(processed_abs_path, pad_color=pad_color)

    # 4. Compute geometry in pixels
    # Convert normalised bbox to pixels for explicit geometry fields
    px_min = bbox_norm["x_min"] * w
    px_max = bbox_norm["x_max"] * w
    py_min = bbox_norm["y_min"] * h
    py_max = bbox_norm["y_max"] * h

    garment_width = round(px_max - px_min)
    garment_height = round(py_max - py_min)
    center_x = round((px_min + px_max) / 2.0)
    center_y = round((py_min + py_max) / 2.0)

    logger.info("Garment processing complete for %s (%s)", clothing_id, source_type)

    return {
        "clothing_id": clothing_id,
        "source_type": source_type,
        "category": category,
        "original_image": prep_result["original_path"],
        "processed_image": prep_result["processed_path"],
        "geometry": {
            "image_width": w,
            "image_height": h,
            "image_format": img_format,
            "color_mode": img_mode,
            "aspect_ratio": aspect_ratio,
            "bounding_box": bbox_norm,
            "garment_width": garment_width,
            "garment_height": garment_height,
            "center": {
                "x": center_x,
                "y": center_y
            }
        }
    }
