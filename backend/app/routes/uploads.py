from flask import Blueprint, request
from app.services.upload_service import validate_and_save_image, UploadServiceError
from app.utils.response import success_response, error_response
from app.utils.decorators import jwt_required, admin_required

uploads_bp = Blueprint('uploads', __name__)

@uploads_bp.route('/user-image', methods=['POST'])
@jwt_required()
def upload_user_image(current_user):
    """Upload an image of the user for virtual try-on."""
    if 'image' not in request.files:
        return error_response("No image file in request", 400, {"code": "MISSING_IMAGE"})
        
    file_obj = request.files['image']
    try:
        data = validate_and_save_image(file_obj, 'users')
        data['type'] = 'user_image'
        return success_response(
            message="User image uploaded successfully",
            data=data
        )
    except UploadServiceError as e:
        return error_response(e.message, 400, {"code": e.code})
    except Exception as e:
        return error_response("Upload failed", 500, {"code": "INTERNAL_ERROR"})

@uploads_bp.route('/clothing-image', methods=['POST'])
@jwt_required()
@admin_required()
def upload_catalog_image(current_user):
    """Upload an image for the global admin clothing catalog."""
    if 'image' not in request.files:
        return error_response("No image file in request", 400, {"code": "MISSING_IMAGE"})
        
    file_obj = request.files['image']
    try:
        data = validate_and_save_image(file_obj, 'catalog')
        data['type'] = 'catalog_image'
        return success_response(
            message="Catalog clothing image uploaded successfully",
            data=data
        )
    except UploadServiceError as e:
        return error_response(e.message, 400, {"code": e.code})
    except Exception as e:
        return error_response("Upload failed", 500, {"code": "INTERNAL_ERROR"})
