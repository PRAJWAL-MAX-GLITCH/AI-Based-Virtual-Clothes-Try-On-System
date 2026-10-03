from flask import Blueprint, request, current_app
from app.services.pipeline_service import TryOnPipeline, PipelineServiceError
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required

tryon_bp = Blueprint('tryon', __name__)

@tryon_bp.route('', methods=['POST'])
@jwt_required()
def tryon(current_user):
    """
    Perform 2D Virtual Try-On by orchestrating the complete pipeline.

    Request body (JSON):
    {
        "person_image_id": "<path to preprocessed person image>",
        "clothing_id": "<mongodb_id_of_clothing_or_user_clothing>"
    }
    """
    data = request.get_json() or {}
    person_image_id = data.get('person_image_id', '').strip()
    clothing_id_str = data.get('clothing_id', '').strip()

    if not person_image_id or not clothing_id_str:
        return error_response("Both person_image_id and clothing_id are required", 400, {"code": "MISSING_PARAMS"})

    try:
        pipeline = TryOnPipeline(current_user)
        result = pipeline.run(person_image_id, clothing_id_str)
        # Note: pipeline.run returns the full success structured dictionary directly
        return result, 200
    except PipelineServiceError as exc:
        status = 404 if exc.code in ("PERSON_IMAGE_NOT_FOUND", "CLOTHING_NOT_FOUND", "NOT_FOUND") else (403 if exc.code in ("UNAUTHORIZED_CLOTHING", "FORBIDDEN") else 400)
        return error_response(exc.message, status, {"code": exc.code})
    except Exception as exc:
        current_app.logger.error(f"Virtual try-on failed: {exc}")
        return error_response("Virtual try-on could not be completed", 500, {"code": "TRYON_PIPELINE_FAILED"})
