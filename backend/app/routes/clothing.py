from flask import Blueprint, request
from app.services.clothing_service import (
    create_clothing,
    get_clothing_list,
    get_clothing_by_id,
    update_clothing,
    deactivate_clothing,
    associate_image_with_clothing,
    ClothingServiceError
)
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required, admin_required

clothing_bp = Blueprint('clothing', __name__)

@clothing_bp.route('', methods=['POST'])
@jwt_required()
@admin_required()
def create(current_user):
    data = request.get_json() or {}
    try:
        item = create_clothing(data, current_user['id'])
        return success_response(
            message="Clothing item created successfully",
            status_code=201,
            data={"clothing": item}
        )
    except ClothingServiceError as e:
        return error_response(message=e.message, status_code=400, error={"code": e.code})

@clothing_bp.route('', methods=['GET'])
@jwt_required()
def list_clothing(current_user):
    # args is a MultiDict, convert safely to normal dict for service
    query_params = {k: v for k, v in request.args.items()}
    try:
        result = get_clothing_list(query_params)
        return success_response(
            message="Clothing catalog retrieved successfully",
            data=result
        )
    except Exception as e:
        return error_response(message="Failed to retrieve catalog", status_code=400, error={"code": "INVALID_QUERY"})

@clothing_bp.route('/<clothing_id>', methods=['GET'])
@jwt_required()
def get_single(current_user, clothing_id):
    try:
        item = get_clothing_by_id(clothing_id)
        return success_response(
            message="Clothing item retrieved successfully",
            data={"clothing": item}
        )
    except ClothingServiceError as e:
        status_code = 404 if e.code == "CLOTHING_NOT_FOUND" else 400
        return error_response(message=e.message, status_code=status_code, error={"code": e.code})

@clothing_bp.route('/<clothing_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update(current_user, clothing_id):
    data = request.get_json() or {}
    try:
        item = update_clothing(clothing_id, data)
        return success_response(
            message="Clothing item updated successfully",
            data={"clothing": item}
        )
    except ClothingServiceError as e:
        status_code = 404 if e.code == "CLOTHING_NOT_FOUND" else 400
        return error_response(message=e.message, status_code=status_code, error={"code": e.code})

@clothing_bp.route('/<clothing_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_clothing(current_user, clothing_id):
    try:
        deactivate_clothing(clothing_id)
        return success_response(
            message="Clothing item deactivated successfully"
        )
    except ClothingServiceError as e:
        status_code = 404 if e.code == "CLOTHING_NOT_FOUND" else 400
        return error_response(message=e.message, status_code=status_code, error={"code": e.code})

@clothing_bp.route('/<clothing_id>/image', methods=['PUT'])
@jwt_required()
@admin_required()
def upload_clothing_image(current_user, clothing_id):
    if 'image' not in request.files:
        return error_response("No image file in request", 400, {"code": "MISSING_IMAGE"})
        
    file_obj = request.files['image']
    try:
        from app.services.upload_service import validate_and_save_image, UploadServiceError
        upload_data = validate_and_save_image(file_obj, 'catalog')
        item = associate_image_with_clothing(clothing_id, upload_data['path'])
        
        return success_response(
            message="Clothing image associated successfully",
            data={"clothing": item}
        )
    except UploadServiceError as e:
        return error_response(e.message, 400, {"code": e.code})
    except ClothingServiceError as e:
        status_code = 404 if e.code == "CLOTHING_NOT_FOUND" else 400
        return error_response(e.message, status_code, {"code": e.code})
    except Exception as e:
        return error_response("Upload failed", 500, {"code": "INTERNAL_ERROR"})
