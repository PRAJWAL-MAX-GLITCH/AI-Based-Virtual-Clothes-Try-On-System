"""
app/ai/virtual_tryon.py

Core 2D Try-on/compositing logic.
"""

import os
import logging
from PIL import Image
from flask import current_app

logger = logging.getLogger(__name__)

class VirtualTryonError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)


def composite_tryon(person_image_path: str, aligned_garment_path: str, category: str, transformation: dict) -> dict:
    """
    Perform 2D alpha compositing of the aligned garment onto the person image.
    """
    if not os.path.isfile(person_image_path):
        raise VirtualTryonError("Person image not found", "PERSON_IMAGE_NOT_FOUND")
    if not os.path.isfile(aligned_garment_path):
        raise VirtualTryonError("Aligned garment layer not found", "ALIGNED_GARMENT_NOT_FOUND")

    try:
        person_img = Image.open(person_image_path).convert("RGBA")
    except Exception as e:
        raise VirtualTryonError(f"Failed to load person image: {e}", "IMAGE_LOAD_ERROR")

    try:
        garment_img = Image.open(aligned_garment_path).convert("RGBA")
    except Exception as e:
        raise VirtualTryonError(f"Failed to load aligned garment image: {e}", "IMAGE_LOAD_ERROR")

    person_w, person_h = person_img.size
    garment_w, garment_h = garment_img.size

    if person_w != garment_w or person_h != garment_h:
        logger.warning(f"Dimension mismatch during compositing. Person: {person_w}x{person_h}, Garment: {garment_w}x{garment_h}")
        # Resize garment canvas to match person canvas if needed
        garment_img = garment_img.resize((person_w, person_h), Image.Resampling.LANCZOS)

    # Perform alpha compositing
    # Image.alpha_composite requires both images to be RGBA and the same size
    try:
        result_img = Image.alpha_composite(person_img, garment_img)
        # Convert back to RGB to save as standard image if preferred, but PNG supports RGBA.
        # We will keep RGBA or convert to RGB. 
        # The prompt says "The final result should normally be RGB or RGBA as appropriate... Prefer PNG".
        # Let's save as RGBA to be safe and preserve any background transparency if the person image had it.
    except Exception as e:
        raise VirtualTryonError(f"Compositing failed: {e}", "COMPOSITING_FAILED")

    # Save output
    import uuid
    upload_root = current_app.config['UPLOAD_FOLDER']
    results_dir = os.path.join(upload_root, 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    filename = f"tryon_{uuid.uuid4().hex}.png"
    output_abs_path = os.path.join(results_dir, filename)
    
    try:
        result_img.save(output_abs_path, format="PNG")
        # Re-open to verify
        Image.open(output_abs_path).verify()
    except Exception as e:
        # cleanup invalid output if exists
        if os.path.exists(output_abs_path):
            os.remove(output_abs_path)
        raise VirtualTryonError(f"Failed to save generated result: {e}", "SAVE_ERROR")

    output_rel_path = f"results/{filename}"

    return {
        "success": True,
        "result_image": output_rel_path,
        "category": category,
        "image_size": {
            "width": person_w,
            "height": person_h
        },
        "transformation": transformation
    }
