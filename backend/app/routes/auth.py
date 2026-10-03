from flask import Blueprint, request
from app.services.auth_service import register_user, login_user, AuthServiceError
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    try:
        user_data = register_user(data)
        return success_response(
            message="User registered successfully",
            status_code=201,
            data={"user": user_data}
        )
    except AuthServiceError as e:
        # Map specific codes to HTTP statuses
        status = 409 if e.code == "EMAIL_ALREADY_EXISTS" else 400
        return error_response(
            message=e.message,
            status_code=status,
            error={"code": e.code}
        )
    except Exception as e:
        return error_response(
            message="An unexpected error occurred during registration",
            status_code=500,
            error={"code": "INTERNAL_ERROR"}
        )

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    try:
        login_data = login_user(data)
        return success_response(
            message="Login successful",
            data=login_data
        )
    except AuthServiceError as e:
        status = 403 if e.code == "ACCOUNT_INACTIVE" else 401
        return error_response(
            message=e.message,
            status_code=status,
            error={"code": e.code}
        )
    except Exception as e:
        return error_response(
            message="An unexpected error occurred during login",
            status_code=500,
            error={"code": "INTERNAL_ERROR"}
        )

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def current_user(current_user):
    """Returns the authenticated user's details."""
    return success_response(
        message="Current user retrieved successfully",
        data={"user": current_user}
    )
