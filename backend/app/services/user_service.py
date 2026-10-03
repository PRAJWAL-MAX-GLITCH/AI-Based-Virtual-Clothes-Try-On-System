import datetime
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from app.extensions import mongo
from app.models.user import serialize_user
from app.utils.validators import validate_email, validate_name, validate_password, normalize_email

class UserServiceError(Exception):
    """Custom exception for user service failures."""
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)

def get_user_profile(user_id):
    """Retrieves the current user's profile."""
    users_col = mongo.get_collection('users')
    user_doc = users_col.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise UserServiceError("User not found", "USER_NOT_FOUND")
    return serialize_user(user_doc)

def update_user_profile(user_id, data):
    """Updates user's name and email."""
    name = data.get('name')
    email = data.get('email')
    profile_image_path = data.get('profile_image_path')
    phone = data.get('phone')
    location = data.get('location')
    
    update_fields = {}
    
    if name is not None:
        if not validate_name(name):
            raise UserServiceError("Invalid name length", "INVALID_NAME")
        update_fields['name'] = name.strip()
        
    if email is not None:
        if not validate_email(email):
            raise UserServiceError("Invalid email format", "INVALID_EMAIL")
        update_fields['email'] = normalize_email(email)

    if profile_image_path is not None:
        update_fields['profile_image_path'] = profile_image_path

    if phone is not None:
        update_fields['phone'] = phone.strip()

    if location is not None:
        update_fields['location'] = location.strip()
        
    if not update_fields:
        raise UserServiceError("No valid fields provided for update", "NO_UPDATES_PROVIDED")
        
    users_col = mongo.get_collection('users')
    
    # Check if the fields are actually different from existing
    current_user = users_col.find_one({"_id": ObjectId(user_id)})
    if not current_user:
        raise UserServiceError("User not found", "USER_NOT_FOUND")
        
    is_changed = False
    for k, v in update_fields.items():
        if current_user.get(k) != v:
            is_changed = True
            break
            
    if not is_changed:
        raise UserServiceError("No fields were changed", "NO_CHANGES_MADE")
        
    update_fields['updated_at'] = datetime.datetime.now(datetime.timezone.utc)
    
    try:
        users_col.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_fields}
        )
        # Fetch and return updated
        updated_doc = users_col.find_one({"_id": ObjectId(user_id)})
        return serialize_user(updated_doc)
    except DuplicateKeyError:
        raise UserServiceError("Email is already registered", "EMAIL_ALREADY_EXISTS")

def change_password(user_id, data):
    """Changes user's password."""
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        raise UserServiceError("Current and new passwords are required", "MISSING_PASSWORDS")
        
    if not validate_password(new_password):
        raise UserServiceError("New password must be at least 8 characters", "WEAK_PASSWORD")
        
    users_col = mongo.get_collection('users')
    user_doc = users_col.find_one({"_id": ObjectId(user_id)})
    
    if not user_doc:
        raise UserServiceError("User not found", "USER_NOT_FOUND")
        
    if not check_password_hash(user_doc['password_hash'], current_password):
        raise UserServiceError("Incorrect current password", "INCORRECT_PASSWORD")
        
    new_hash = generate_password_hash(new_password)
    now = datetime.datetime.now(datetime.timezone.utc)
    
    users_col.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": new_hash, "updated_at": now}}
    )
    
def deactivate_account(user_id):
    """Deactivates a user's account by setting is_active to false."""
    users_col = mongo.get_collection('users')
    now = datetime.datetime.now(datetime.timezone.utc)
    
    result = users_col.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": False, "updated_at": now}}
    )
    
    if result.matched_count == 0:
        raise UserServiceError("User not found", "USER_NOT_FOUND")
