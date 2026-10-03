from flask import Blueprint, request, current_app
from app.services.history_service import (
    get_history,
    get_single_history,
    delete_history,
    get_history_result,
    HistoryServiceError
)
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required

history_bp = Blueprint('history', __name__)

def _handle_error(exc: Exception):
    if isinstance(exc, HistoryServiceError):
        status = 404 if exc.code in ("NOT_FOUND", "NO_RESULT_IMAGE") else (403 if exc.code == "FORBIDDEN" else 400)
        return error_response(exc.message, status, {"code": exc.code})
    current_app.logger.error(f"History endpoint error: {exc}")
    return error_response("Internal Server Error", 500, {"code": "INTERNAL_ERROR"})

@history_bp.route('', methods=['GET'])
@jwt_required()
def list_history(current_user):
    """
    Retrieve paginated try-on history for the authenticated user.
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        result = get_history(current_user, page, limit)
        return success_response(data=result, message="Try-on history retrieved successfully")
    except ValueError:
        return error_response("Invalid pagination parameters", 400, {"code": "INVALID_PARAMS"})
    except Exception as exc:
        return _handle_error(exc)

@history_bp.route('/<history_id>', methods=['GET'])
@jwt_required()
def get_history_item(current_user, history_id):
    """
    Retrieve a specific history record.
    """
    try:
        result = get_single_history(history_id, current_user)
        return success_response(data=result, message="History record retrieved successfully")
    except Exception as exc:
        return _handle_error(exc)

@history_bp.route('/<history_id>', methods=['DELETE'])
@jwt_required()
def delete_history_item(current_user, history_id):
    """
    Delete a history record and its associated result image.
    """
    try:
        result = delete_history(history_id, current_user)
        return success_response(data=None, message=result["message"])
    except Exception as exc:
        return _handle_error(exc)

@history_bp.route('/<history_id>/result', methods=['GET'])
@jwt_required()
def get_history_result_url(current_user, history_id):
    """
    Retrieve a secure URL for the generated result image.
    """
    try:
        result = get_history_result(history_id, current_user)
        return success_response(data=result, message="Result retrieved successfully")
    except Exception as exc:
        return _handle_error(exc)
