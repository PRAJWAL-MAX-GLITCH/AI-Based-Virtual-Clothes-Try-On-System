"""
app/routes/processing.py

POST /api/v1/processing/preview

Accepts a reference to an already-uploaded image (stored relative path or
a user_clothing_id) and runs the preprocessing pipeline on it.

Security rules
--------------
- User can only preprocess their own uploads (person image, user clothing).
- Admin can preprocess catalog clothing via a clothing_id reference.
- No arbitrary filesystem paths are accepted from the client.
"""

from flask import Blueprint, request
from app.ai.preprocessing import (
    preprocess_person_image,
    preprocess_clothing_image,
    PreprocessingError,
)
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required
from flask import current_app
import os

processing_bp = Blueprint('processing', __name__)


def _safe_path_in_upload_root(relative_path: str) -> bool:
    """Return True if relative_path stays inside the upload root."""
    upload_root = current_app.config['UPLOAD_FOLDER']
    normalized  = os.path.normpath(relative_path)
    if normalized.startswith('..'):
        return False
    full = os.path.join(upload_root, normalized)
    return os.path.abspath(full).startswith(os.path.abspath(upload_root))


@processing_bp.route('/preview', methods=['POST'])
@jwt_required()
def preview(current_user):
    """
    Run image preprocessing on an already-uploaded image.

    Request body (JSON):
    {
        "type":         "person" | "clothing",
        "image_path":   "<relative path from UPLOAD_FOLDER>",

        // Optional – only for clothing:
        "preserve_alpha": false
    }

    The image_path must be a relative path previously returned by the upload
    API (e.g. "users/abc123.png" or "clothing/user/xyz.png").  The server
    resolves the real path internally; clients cannot supply absolute paths.

    Ownership enforcement
    ---------------------
    - type == "person"   →  path must start with "users/"
    - type == "clothing" →  path must start with "clothing/"

    For user-type clothing, the ownership was already verified at upload time.
    This endpoint therefore trusts the stored path, not the user-supplied one.
    """
    data = request.get_json() or {}

    image_type  = data.get('type', '').strip()
    image_path  = data.get('image_path', '').strip()
    keep_alpha  = bool(data.get('preserve_alpha', False))

    # ── Input validation ──────────────────────────────────────────────────────
    if image_type not in ('person', 'clothing'):
        return error_response(
            "Invalid type. Must be 'person' or 'clothing'.",
            400,
            {"code": "INVALID_TYPE"}
        )

    if not image_path:
        return error_response("image_path is required", 400, {"code": "MISSING_PATH"})

    # Prevent path traversal / absolute paths
    if not _safe_path_in_upload_root(image_path):
        return error_response("Invalid image path", 400, {"code": "INVALID_PATH"})

    # ── Ownership guard ───────────────────────────────────────────────────────
    # Person images must live under "users/"
    if image_type == 'person' and not image_path.startswith('users/'):
        return error_response(
            "Person image path must reference a user image.",
            403,
            {"code": "FORBIDDEN"}
        )

    # Clothing images must live under "clothing/"
    if image_type == 'clothing' and not image_path.startswith('clothing/'):
        return error_response(
            "Clothing image path must reference a clothing image.",
            403,
            {"code": "FORBIDDEN"}
        )

    # ── Preprocessing ─────────────────────────────────────────────────────────
    try:
        if image_type == 'person':
            result = preprocess_person_image(image_path)
        else:
            result = preprocess_clothing_image(image_path, preserve_alpha=keep_alpha)

        return success_response(
            message="Image preprocessing completed successfully",
            data={
                "type":            result["type"],
                "processed_image": result["processed_path"],
                "metadata": {
                    "original_size":   result["original_size"],
                    "processed_size":  result["processed_size"],
                    "format":          result["format"],
                    "mode":            result["mode"],
                    "scale":           result["scale"],
                    "padding":         result["padding"],
                }
            }
        )

    except PreprocessingError as exc:
        status = 404 if exc.code in ("IMAGE_NOT_FOUND",) else 400
        return error_response(exc.message, status, {"code": exc.code})
    except Exception as exc:
        current_app.logger.error("Preprocessing failed: %s", exc)
        return error_response("Preprocessing failed", 500, {"code": "INTERNAL_ERROR"})


@processing_bp.route('/pose', methods=['POST'])
@jwt_required()
def pose(current_user):
    """
    Run MediaPipe pose detection + basic body analysis on a preprocessed
    person image.

    Request body (JSON):
    {
        "image_path": "<relative path under UPLOAD_FOLDER, must start with 'processed/users/'>"
    }

    The image_path must be the processed path returned by POST /processing/preview
    (i.e. the output of the preprocessing stage, NOT the raw upload).

    Security
    --------
    - Authentication required.
    - Path must resolve inside UPLOAD_FOLDER (traversal guard).
    - Path must start with 'processed/users/' (person images only –
      catalog/clothing images are NOT valid inputs for pose detection).
    """
    import os
    from app.ai.pose_detection import detect_pose, PoseDetectionError
    from app.ai.body_analysis  import analyse_body,  BodyAnalysisError

    data       = request.get_json() or {}
    image_path = data.get('image_path', '').strip()

    # ── Input validation ──────────────────────────────────────────────────────
    if not image_path:
        return error_response("image_path is required", 400, {"code": "MISSING_PATH"})

    if not _safe_path_in_upload_root(image_path):
        return error_response("Invalid image path", 400, {"code": "INVALID_PATH"})

    # Only preprocessed person images are valid pose-detection inputs.
    if not image_path.startswith('processed/users/'):
        return error_response(
            "image_path must reference a preprocessed person image "
            "(must start with 'processed/users/').",
            403,
            {"code": "FORBIDDEN"}
        )

    # Resolve absolute path
    upload_root = current_app.config['UPLOAD_FOLDER']
    abs_path    = os.path.join(upload_root, os.path.normpath(image_path))

    # ── Pose detection ────────────────────────────────────────────────────────
    try:
        pose_result = detect_pose(abs_path)
    except PoseDetectionError as exc:
        status = 404 if exc.code == "IMAGE_NOT_FOUND" else 400
        return error_response(exc.message, status, {"code": exc.code})
    except Exception as exc:
        current_app.logger.error("Pose detection failed: %s", exc)
        return error_response("Pose detection failed", 500, {"code": "INTERNAL_ERROR"})

    if not pose_result.get("person_detected"):
        return success_response(
            message="No person detected in image",
            data={
                "person_detected":  False,
                "landmarks":        [],
                "body_analysis":    None,
            }
        )

    # ── Body analysis ─────────────────────────────────────────────────────────
    try:
        body_info = analyse_body(pose_result)
    except BodyAnalysisError as exc:
        # Pose succeeded but essential landmarks missing – return partial result
        return success_response(
            message="Pose detected but body analysis incomplete",
            data={
                "person_detected":     True,
                "landmarks":           pose_result.get("landmarks", []),
                "important_landmarks": pose_result.get("important_landmarks", {}),
                "detection_quality":   pose_result.get("detection_quality", {}),
                "body_analysis":       None,
                "body_analysis_error": exc.message,
            }
        )
    except Exception as exc:
        current_app.logger.error("Body analysis failed: %s", exc)
        return error_response("Body analysis failed", 500, {"code": "INTERNAL_ERROR"})

    return success_response(
        message="Pose detection completed successfully",
        data={
            "person_detected":     True,
            "landmarks":           pose_result["landmarks"],
            "important_landmarks": pose_result["important_landmarks"],
            "detection_quality":   pose_result["detection_quality"],
            "image_width":         pose_result["image_width"],
            "image_height":        pose_result["image_height"],
            "body_analysis":       body_info,
        }
    )


@processing_bp.route('/garment', methods=['POST'])
@jwt_required()
def garment(current_user):
    """
    Run garment processing on a previously uploaded clothing item.

    Request body (JSON):
    {
        "clothing_id": "<mongodb_id_of_clothing_or_user_clothing>"
    }

    The backend resolves the DB record, checks access rules, retrieves the
    stored original image, runs preprocessing (to normalise size/transparency),
    and finally computes garment geometry properties.
    """
    from bson.objectid import ObjectId
    from bson.errors import InvalidId
    from app.extensions import mongo
    from app.ai.garment_processing import process_garment, GarmentProcessingError

    data = request.get_json() or {}
    clothing_id_str = data.get('clothing_id', '').strip()

    if not clothing_id_str:
        return error_response("clothing_id is required", 400, {"code": "MISSING_CLOTHING_ID"})

    try:
        clothing_id = ObjectId(clothing_id_str)
    except InvalidId:
        return error_response("Invalid clothing_id format", 400, {"code": "INVALID_ID"})

    db = mongo.get_db()

    # 1. Try to find in admin catalog clothing
    clothing_record = db.clothing.find_one({"_id": clothing_id})
    if clothing_record:
        # Catalog clothing: Users can process it
        source_type = "catalog"
    else:
        # 2. Try to find in user custom clothing
        clothing_record = db.user_clothing.find_one({"_id": clothing_id})
        if not clothing_record:
            return error_response("Clothing item not found", 404, {"code": "NOT_FOUND"})

        # Verify ownership: User A cannot process User B's custom clothing
        if str(clothing_record.get("user_id")) != current_user["id"]:
            return error_response(
                "You do not have permission to process this custom clothing item.",
                403,
                {"code": "FORBIDDEN"}
            )
        source_type = "user_custom"

    image_path = clothing_record.get("image")
    if not image_path:
        return error_response("Clothing item has no associated image file", 400, {"code": "MISSING_IMAGE"})

    category = clothing_record.get("category", "unknown")

    # 3. Process garment
    try:
        result = process_garment(clothing_id_str, image_path, source_type, category)
        return success_response(
            message="Garment processing completed successfully",
            data=result
        )
    except GarmentProcessingError as exc:
        status = 404 if exc.code in ("IMAGE_READ_ERROR", "IMAGE_NOT_FOUND") else 400
        return error_response(exc.message, status, {"code": exc.code})
    except Exception as exc:
        current_app.logger.error("Garment processing failed: %s", exc)
        return error_response("Garment processing failed", 500, {"code": "INTERNAL_ERROR"})


@processing_bp.route('/align-garment', methods=['POST'])
@jwt_required()
def align_garment_endpoint(current_user):
    """
    Perform 2D geometric alignment of a garment onto a person's upper body.

    Request body (JSON):
    {
        "person_image_id": "<path to preprocessed person image>",
        "clothing_id": "<mongodb_id_of_clothing_or_user_clothing>"
    }
    """
    from app.services.alignment_service import perform_garment_alignment, AlignmentServiceError
    
    data = request.get_json() or {}
    person_image_id = data.get('person_image_id', '').strip()
    clothing_id_str = data.get('clothing_id', '').strip()

    if not person_image_id or not clothing_id_str:
        return error_response("Both person_image_id and clothing_id are required", 400, {"code": "MISSING_PARAMS"})

    try:
        result = perform_garment_alignment(person_image_id, clothing_id_str, current_user)
        return success_response(
            message="Garment alignment completed successfully",
            data=result
        )
    except AlignmentServiceError as exc:
        status = 404 if exc.code in ("NOT_FOUND", "PERSON_NOT_FOUND", "IMAGE_NOT_FOUND") else (403 if exc.code == "FORBIDDEN" else 400)
        return error_response(exc.message, status, {"code": exc.code})
    except Exception as exc:
        current_app.logger.error(f"Alignment failed: {exc}")
        return error_response("Garment alignment failed", 500, {"code": "INTERNAL_ERROR"})
