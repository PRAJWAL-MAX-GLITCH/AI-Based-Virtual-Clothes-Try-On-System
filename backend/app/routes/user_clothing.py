from flask import Blueprint, request
from app.services.user_clothing_service import (
    create_user_clothing,
    get_user_clothing_list,
    get_user_clothing_by_id,
    delete_user_clothing,
    UserClothingServiceError
)
from app.services.upload_service import validate_and_save_image, UploadServiceError
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required

user_clothing_bp = Blueprint('user_clothing', __name__)

@user_clothing_bp.route('', methods=['POST'])
@jwt_required()
def create_custom_clothing(current_user):
    if 'image' not in request.files:
        return error_response("No image file in request", 400, {"code": "MISSING_IMAGE"})
        
    file_obj = request.files['image']
    data = dict(request.form)
    
    try:
        # Validate and save image first
        upload_data = validate_and_save_image(file_obj, 'user_clothing')
        image_path = upload_data['path']
        
        # Create db record
        item = create_user_clothing(current_user['id'], data, image_path)
        return success_response(
            message="Custom clothing uploaded successfully",
            status_code=201,
            data={"clothing": item}
        )
    except UploadServiceError as e:
        return error_response(e.message, 400, {"code": e.code})
    except UserClothingServiceError as e:
        return error_response(e.message, 400, {"code": e.code})
    except Exception as e:
        return error_response("Failed to upload custom clothing", 500, {"code": "INTERNAL_ERROR"})

@user_clothing_bp.route('', methods=['GET'])
@jwt_required()
def list_custom_clothing(current_user):
    try:
        items = get_user_clothing_list(current_user['id'])
        return success_response(
            message="Custom clothing retrieved successfully",
            data={"items": items}
        )
    except Exception as e:
        return error_response("Failed to retrieve custom clothing", 500, {"code": "INTERNAL_ERROR"})

@user_clothing_bp.route('/<clothing_id>', methods=['GET'])
@jwt_required()
def get_custom_clothing(current_user, clothing_id):
    try:
        item = get_user_clothing_by_id(current_user['id'], clothing_id)
        return success_response(
            message="Custom clothing retrieved successfully",
            data={"clothing": item}
        )
    except UserClothingServiceError as e:
        status_code = 404 if e.code == "CLOTHING_NOT_FOUND" else 400
        return error_response(e.message, status_code, {"code": e.code})

@user_clothing_bp.route('/<clothing_id>', methods=['DELETE'])
@jwt_required()
def delete_custom_clothing(current_user, clothing_id):
    try:
        delete_user_clothing(current_user['id'], clothing_id)
        return success_response(message="Custom clothing deleted successfully")
    except UserClothingServiceError as e:
        status_code = 404 if e.code == "CLOTHING_NOT_FOUND" else 400
        return error_response(e.message, status_code, {"code": e.code})
