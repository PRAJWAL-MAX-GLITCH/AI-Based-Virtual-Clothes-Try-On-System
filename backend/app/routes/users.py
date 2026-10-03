from flask import Blueprint, request
from app.services.user_service import (
    get_user_profile, 
    update_user_profile, 
    change_password, 
    deactivate_account, 
    UserServiceError
)
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me(current_user):
    """Returns the authenticated user's profile."""
    try:
        user_data = get_user_profile(current_user['id'])
        return success_response(
            message="Profile retrieved successfully",
            data={"user": user_data}
        )
    except UserServiceError as e:
        return error_response(message=e.message, status_code=404, error={"code": e.code})

@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me(current_user):
    """Updates the user's name and/or email."""
    data = request.get_json() or {}
    try:
        updated_user = update_user_profile(current_user['id'], data)
        return success_response(
            message="Profile updated successfully",
            data={"user": updated_user}
        )
    except UserServiceError as e:
        status_code = 409 if e.code == "EMAIL_ALREADY_EXISTS" else 400
        return error_response(message=e.message, status_code=status_code, error={"code": e.code})

@users_bp.route('/me/password', methods=['PATCH'])
@jwt_required()
def update_password(current_user):
    """Changes the user's password."""
    data = request.get_json() or {}
    try:
        change_password(current_user['id'], data)
        return success_response(message="Password changed successfully")
    except UserServiceError as e:
        # Prevent leaking if it's incorrect password, just return standard 400 or 403
        status_code = 403 if e.code == "INCORRECT_PASSWORD" else 400
        return error_response(message=e.message, status_code=status_code, error={"code": e.code})

@users_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_me(current_user):
    """Deactivates the user's account."""
    try:
        deactivate_account(current_user['id'])
        return success_response(message="Account deactivated successfully")
    except UserServiceError as e:
        return error_response(message=e.message, status_code=400, error={"code": e.code})
