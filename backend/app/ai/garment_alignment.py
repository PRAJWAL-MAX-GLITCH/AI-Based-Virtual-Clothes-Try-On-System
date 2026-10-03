"""
app/ai/garment_alignment.py

2D Garment Alignment module.
Scales, rotates, and positions a processed garment image over a person's upper body.

CURRENT STAGE: 2D geometric alignment.
NOT IMPLEMENTED: 3D modeling, cloth simulation, warping, final compositing, occlusion handling.
"""

import os
import logging
from PIL import Image
from flask import current_app

logger = logging.getLogger(__name__)

# Basic category-specific multipliers for alignment
# (A real garment is usually slightly wider than the exact distance between shoulder joints)
GARMENT_ALIGNMENT_CONFIG = {
    "t-shirt": {"scale_multiplier": 1.4,  "y_offset_multiplier": -0.1},
    "shirt":   {"scale_multiplier": 1.4,  "y_offset_multiplier": -0.1},
    "hoodie":  {"scale_multiplier": 1.6,  "y_offset_multiplier": -0.15},
    "jacket":  {"scale_multiplier": 1.5,  "y_offset_multiplier": -0.15},
    "top":     {"scale_multiplier": 1.3,  "y_offset_multiplier": -0.05},
    "dress":   {"scale_multiplier": 1.35, "y_offset_multiplier": -0.1},
    "default": {"scale_multiplier": 1.4,  "y_offset_multiplier": -0.1}
}


class GarmentAlignmentError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code    = code
        super().__init__(message)


def align_garment(person_image_path: str, pose_result: dict, garment_image_path: str, garment_geometry: dict, category: str) -> dict:
    """
    Perform 2D geometric alignment of a garment onto a person's body.
    """
    # 1. Validation
    if not os.path.isfile(person_image_path):
        raise GarmentAlignmentError("Person image not found", "PERSON_IMAGE_NOT_FOUND")
    if not os.path.isfile(garment_image_path):
        raise GarmentAlignmentError("Garment image not found", "GARMENT_IMAGE_NOT_FOUND")

    if not pose_result.get("person_detected") or not pose_result.get("body_analysis"):
        raise GarmentAlignmentError("Unable to align garment because required body landmarks were not detected.", "INSUFFICIENT_POSE_DATA")

    body_analysis = pose_result["body_analysis"]
    person_w = pose_result.get("image_width", 768)
    person_h = pose_result.get("image_height", 1024)

    # 2. Extract Body Target Geometry
    # Body analysis uses normalised coordinates (0.0 - 1.0). Convert to pixels.
    try:
        norm_shoulder_width = body_analysis["shoulder_width"]
        norm_shoulder_center = body_analysis["shoulder_center"]
        shoulder_angle = body_analysis["shoulder_angle"]
    except KeyError as e:
        raise GarmentAlignmentError(f"Missing body geometry data: {e}", "INCOMPLETE_BODY_DATA")

    target_shoulder_width_px = norm_shoulder_width * person_w
    target_center_x_px = norm_shoulder_center["x"] * person_w
    target_center_y_px = norm_shoulder_center["y"] * person_h

    # Protect against bad pose data (e.g. extreme rotations)
    MAX_ROTATION = 35.0
    if abs(shoulder_angle) > MAX_ROTATION:
        logger.warning(f"Extreme shoulder angle ({shoulder_angle} deg) clamped to {MAX_ROTATION}")
        rotation_degrees = MAX_ROTATION if shoulder_angle > 0 else -MAX_ROTATION
    else:
        rotation_degrees = shoulder_angle

    # 3. Extract Garment Geometry
    garment_w = garment_geometry.get("garment_width")
    if not garment_w or garment_w <= 0:
        raise GarmentAlignmentError("Invalid garment geometry width", "INVALID_GARMENT_GEOMETRY")

    # 4. Calculate Scale
    cat = category.lower() if category else "default"
    config = GARMENT_ALIGNMENT_CONFIG.get(cat, GARMENT_ALIGNMENT_CONFIG["default"])
    
    scale_multiplier = config["scale_multiplier"]
    base_scale = target_shoulder_width_px / float(garment_w)
    final_scale = base_scale * scale_multiplier

    if final_scale <= 0 or final_scale > 10:
        raise GarmentAlignmentError(f"Unreasonable garment scale calculated: {final_scale}", "INVALID_SCALE")

    # 5. Image Transformation
    try:
        g_img = Image.open(garment_image_path)
        g_img = g_img.convert("RGBA")  # Ensure RGBA for transparency
    except Exception as e:
        raise GarmentAlignmentError(f"Failed to load garment image: {e}", "IMAGE_LOAD_ERROR")

    orig_g_w, orig_g_h = g_img.size

    # Uniform resize
    new_w = int(orig_g_w * final_scale)
    new_h = int(orig_g_h * final_scale)
    if new_w <= 0 or new_h <= 0:
        raise GarmentAlignmentError("Garment scaled to 0 pixels", "INVALID_SCALE")
        
    g_img_resized = g_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Rotation (negative angle because PIL rotation is counter-clockwise, and image coordinates are y-down)
    # Actually, angle_between_points: dy = right.y - left.y, dx = right.x - left.x
    # Positive angle means right shoulder is lower (higher Y).
    # To match this in PIL, we rotate by -angle so it rotates clockwise.
    g_img_rotated = g_img_resized.rotate(-rotation_degrees, resample=Image.Resampling.BICUBIC, expand=True)
    rot_w, rot_h = g_img_rotated.size

    # 6. Calculate Placement
    # Where should the center of the rotated garment image be placed on the person canvas?
    # We map the garment's bounding box center to the body's shoulder center.
    g_center = garment_geometry["center"]
    g_center_x_scaled = g_center["x"] * final_scale
    g_center_y_scaled = g_center["y"] * final_scale

    # After rotation, the center of the image shifts.
    # We assume the center of the bounding box is close to the center of the image.
    # For a simple 2D approximation, aligning the geometric center of the rotated image
    # with the target point (with some Y offset) works well.
    y_offset = config["y_offset_multiplier"] * target_shoulder_width_px

    # Top-left coordinates for pasting the rotated image onto the person canvas
    paste_x = int(target_center_x_px - (rot_w / 2.0))
    paste_y = int(target_center_y_px - (rot_h / 2.0) + y_offset)

    # 7. Create Transparent Canvas
    final_canvas = Image.new("RGBA", (person_w, person_h), (0, 0, 0, 0))
    final_canvas.paste(g_img_rotated, (paste_x, paste_y), g_img_rotated)

    # 8. Save output
    import uuid
    upload_root = current_app.config['UPLOAD_FOLDER']
    aligned_dir = os.path.join(upload_root, 'processed', 'aligned', 'garments')
    os.makedirs(aligned_dir, exist_ok=True)
    
    filename = f"aligned_{uuid.uuid4().hex}.png"
    output_abs_path = os.path.join(aligned_dir, filename)
    
    try:
        final_canvas.save(output_abs_path, format="PNG")
    except Exception as e:
        raise GarmentAlignmentError(f"Failed to save aligned garment: {e}", "SAVE_ERROR")

    output_rel_path = f"processed/aligned/garments/{filename}"

    return {
        "success": True,
        "category": category,
        "aligned_garment": output_rel_path,
        "transformation": {
            "scale": round(final_scale, 4),
            "rotation_degrees": round(rotation_degrees, 4),
            "position": {
                "x": int(target_center_x_px),
                "y": int(target_center_y_px + y_offset)
            }
        },
        "target_geometry": {
            "shoulder_width": round(target_shoulder_width_px, 2),
            "shoulder_center": {
                "x": round(target_center_x_px, 2),
                "y": round(target_center_y_px, 2)
            }
        },
        "source_geometry": {
            "source_width": orig_g_w,
            "source_height": orig_g_h,
            "garment_width": garment_w
        }
    }
