"""
app/utils/image_utils.py

Low-level, reusable image operations built on Pillow.
No business logic lives here – only pure image manipulation helpers.

Future stages (OpenCV, MediaPipe, etc.) will import these helpers or add
their own alongside without touching the existing logic.
"""

import os
import uuid
import logging
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Exceptions
# ──────────────────────────────────────────────────────────────────────────────

class ImageUtilsError(Exception):
    """Raised for validation / processing failures in this module."""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)


# ──────────────────────────────────────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────────────────────────────────────

def validate_image_file(path: str, min_width: int = 64, min_height: int = 64) -> Image.Image:
    """
    Open and validate an image file from disk.

    Checks performed:
    - File exists
    - File is a valid image (Pillow can decode it)
    - Dimensions meet the minimum requirements
    - Image mode is not completely unknown/broken

    Returns the opened PIL Image (ready for further processing).
    Raises ImageUtilsError on any failure.
    """
    if not os.path.isfile(path):
        raise ImageUtilsError("Image file not found", "IMAGE_NOT_FOUND")

    try:
        img = Image.open(path)
        img.verify()          # detects truncated / corrupted files
    except (IOError, SyntaxError, UnidentifiedImageError) as exc:
        logger.warning("Corrupted or invalid image at %s: %s", path, exc)
        raise ImageUtilsError("Invalid or corrupted image", "CORRUPTED_IMAGE")

    # Re-open after verify() (verify() leaves the file in an unusable state)
    try:
        img = Image.open(path)
        img.load()            # force full decode
    except Exception as exc:
        logger.warning("Failed to load image at %s: %s", path, exc)
        raise ImageUtilsError("Failed to load image", "LOAD_ERROR")

    w, h = img.size
    if w < min_width or h < min_height:
        raise ImageUtilsError(
            f"Image too small ({w}x{h}). Minimum: {min_width}x{min_height}.",
            "IMAGE_TOO_SMALL"
        )

    return img


# ──────────────────────────────────────────────────────────────────────────────
# Colour / mode normalisation
# ──────────────────────────────────────────────────────────────────────────────

def to_rgb(img: Image.Image) -> Image.Image:
    """
    Convert an image to RGB, handling common edge-cases:
    - RGBA  → composite onto white background, return RGB
    - L, P, etc. → convert directly to RGB

    The original PIL Image is NOT mutated.
    """
    if img.mode == 'RGB':
        return img

    if img.mode == 'RGBA':
        # Composite the alpha onto a white background so downstream code
        # never has to deal with semi-transparent pixels.
        background = Image.new('RGB', img.size, (255, 255, 255))
        # The mask is the alpha channel of the source image.
        background.paste(img, mask=img.split()[3])
        return background

    # Handles: L, LA, P, CMYK, YCbCr, …
    return img.convert('RGB')


def to_rgba(img: Image.Image) -> Image.Image:
    """
    Convert an image to RGBA, preserving existing alpha if present.
    Used when the caller explicitly wants to retain transparency information
    (e.g. for future garment segmentation).
    """
    if img.mode == 'RGBA':
        return img
    if img.mode == 'RGB':
        return img.convert('RGBA')
    return img.convert('RGBA')


# ──────────────────────────────────────────────────────────────────────────────
# Resizing
# ──────────────────────────────────────────────────────────────────────────────

def resize_keep_aspect_ratio(
    img: Image.Image,
    target_w: int,
    target_h: int,
    resample=Image.LANCZOS
) -> Image.Image:
    """
    Scale `img` so that it fits inside (target_w × target_h) while
    preserving the original aspect ratio.

    The resulting image may be smaller than the target on one axis –
    use resize_and_pad() to place it on a fixed-size canvas.
    """
    orig_w, orig_h = img.size

    scale = min(target_w / orig_w, target_h / orig_h)
    new_w = max(1, round(orig_w * scale))
    new_h = max(1, round(orig_h * scale))

    return img.resize((new_w, new_h), resample=resample), scale


def resize_and_pad(
    img: Image.Image,
    target_w: int,
    target_h: int,
    pad_color=(255, 255, 255),
    resample=Image.LANCZOS
) -> tuple:
    """
    Resize `img` to fit inside (target_w × target_h) with preserved aspect
    ratio, then centre it on a canvas of exactly (target_w × target_h).

    Returns:
        canvas  – the padded PIL Image
        meta    – dict with scale and padding offsets:
                  {
                      "original_width":  int,
                      "original_height": int,
                      "resized_width":   int,
                      "resized_height":  int,
                      "scale":           float,
                      "padding": {
                          "top":    int,
                          "bottom": int,
                          "left":   int,
                          "right":  int,
                      }
                  }
    """
    orig_w, orig_h = img.size

    resized, scale = resize_keep_aspect_ratio(img, target_w, target_h, resample)
    rsz_w, rsz_h = resized.size

    # Determine paste position (centred)
    pad_left   = (target_w - rsz_w) // 2
    pad_top    = (target_h - rsz_h) // 2
    pad_right  = target_w - rsz_w - pad_left
    pad_bottom = target_h - rsz_h - pad_top

    # Build canvas – use RGBA if the resized image has alpha
    mode = resized.mode if resized.mode in ('RGBA',) else 'RGB'
    canvas_bg = pad_color if mode == 'RGB' else pad_color + (255,)
    canvas = Image.new(mode, (target_w, target_h), canvas_bg)
    canvas.paste(resized, (pad_left, pad_top))

    meta = {
        "original_width":  orig_w,
        "original_height": orig_h,
        "resized_width":   rsz_w,
        "resized_height":  rsz_h,
        "scale":           round(scale, 6),
        "padding": {
            "top":    pad_top,
            "bottom": pad_bottom,
            "left":   pad_left,
            "right":  pad_right,
        },
    }

    return canvas, meta


# ──────────────────────────────────────────────────────────────────────────────
# Filename helpers
# ──────────────────────────────────────────────────────────────────────────────

def generate_processed_filename(ext: str = "png") -> str:
    """Generate a secure UUID-based filename for a processed image."""
    return f"proc_{uuid.uuid4().hex}.{ext.lstrip('.')}"


# ──────────────────────────────────────────────────────────────────────────────
# Save
# ──────────────────────────────────────────────────────────────────────────────

def save_image(img: Image.Image, directory: str, filename: str) -> str:
    """
    Save `img` to `directory/filename`.

    - Creates the directory if it does not exist.
    - Strips EXIF / metadata when saving (Pillow default for PNG; explicit
      for JPEG via `subsampling` + no `exif` kwarg).
    - Returns the full absolute path of the saved file.
    - Prevents path traversal vulnerabilities.
    """
    safe_dir = os.path.abspath(directory)
    full_path = os.path.normpath(os.path.join(safe_dir, filename))
    
    if not full_path.startswith(safe_dir):
        raise ImageUtilsError("Path traversal detected", "PATH_TRAVERSAL")
        
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    ext = os.path.splitext(filename)[1].lower()

    if ext in ('.jpg', '.jpeg'):
        # Save as JPEG without passing any EXIF block
        img.save(full_path, format='JPEG', quality=95, optimize=True)
    else:
        # PNG by default – metadata-free by Pillow's standard behaviour
        img.save(full_path, format='PNG', optimize=True)

    return full_path
