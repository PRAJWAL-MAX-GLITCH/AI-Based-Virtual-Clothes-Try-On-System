import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image, UnidentifiedImageError

class UploadServiceError(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)

def get_upload_directories():
    base_dir = current_app.config['UPLOAD_FOLDER']
    directories = {
        'users': os.path.join(base_dir, 'users'),
        'catalog': os.path.join(base_dir, 'clothing', 'catalog'),
        'user_clothing': os.path.join(base_dir, 'clothing', 'user'),
        'results': os.path.join(base_dir, 'results') # Not used yet but initialized
    }
    
    for path in directories.values():
        os.makedirs(path, exist_ok=True)
        
    return directories

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_IMAGE_EXTENSIONS']

def validate_and_save_image(file_obj, upload_type):
    """
    Validates the uploaded file and saves it to the proper directory.
    upload_type options: 'users', 'catalog', 'user_clothing'
    """
    if not file_obj or file_obj.filename == '':
        raise UploadServiceError("No file provided", "NO_FILE")

    if not allowed_file(file_obj.filename):
        raise UploadServiceError("Invalid file extension", "INVALID_EXTENSION")

    # Read bytes to validate image content
    try:
        img = Image.open(file_obj.stream)
        img.verify() # verifies it is an image
        # Reset stream position after verification
        file_obj.stream.seek(0) 
    except (IOError, SyntaxError, UnidentifiedImageError):
        raise UploadServiceError("Invalid or corrupted image data", "CORRUPTED_IMAGE")

    # Ensure upload directories exist
    directories = get_upload_directories()
    
    if upload_type not in directories:
        raise UploadServiceError("Invalid upload type", "INVALID_UPLOAD_TYPE")
        
    target_dir = directories[upload_type]

    # Generate secure UUID-based filename
    ext = file_obj.filename.rsplit('.', 1)[1].lower()
    secure_name = f"{uuid.uuid4().hex}.{ext}"
    
    file_path = os.path.join(target_dir, secure_name)
    
    try:
        file_obj.save(file_path)
    except Exception as e:
        current_app.logger.error(f"Failed to save image: {e}")
        raise UploadServiceError("Failed to save file", "STORAGE_ERROR")

    # Generate a relative path/url reference (mock URL for now, could be an actual endpoint later)
    # The actual static serving can be handled via a route later.
    relative_path = os.path.relpath(file_path, current_app.config['UPLOAD_FOLDER']).replace('\\', '/')
    url = f"/api/v1/static/{relative_path}" 

    return {
        "filename": secure_name,
        "path": relative_path,
        "url": url,
        "type": upload_type
    }

def delete_image(relative_path):
    """Safely deletes an image from the storage."""
    if not relative_path:
        return
        
    base_dir = current_app.config['UPLOAD_FOLDER']
    # Prevent path traversal
    normalized_path = os.path.normpath(relative_path)
    if normalized_path.startswith('..') or os.path.isabs(normalized_path):
        current_app.logger.warning(f"Path traversal attempt detected: {relative_path}")
        return
        
    full_path = os.path.join(base_dir, normalized_path)
    
    # Ensure it's still inside the upload directory
    if not os.path.abspath(full_path).startswith(os.path.abspath(base_dir)):
        current_app.logger.warning(f"Path traversal attempt outside base dir: {relative_path}")
        return

    try:
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        current_app.logger.error(f"Failed to delete file {full_path}: {e}")
