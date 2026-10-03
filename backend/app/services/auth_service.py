import datetime
import jwt
from pymongo.errors import DuplicateKeyError
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app.extensions import mongo
from app.models.user import create_user_document, serialize_user
from app.utils.validators import validate_email, validate_password, validate_name, normalize_email

class AuthServiceError(Exception):
    """Custom exception for auth service failures."""
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(self.message)

def register_user(data):
    """Business logic for user registration."""
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Validation
    if not validate_name(name):
        raise AuthServiceError("Invalid name length", "INVALID_NAME")
    if not validate_email(email):
        raise AuthServiceError("Invalid email format", "INVALID_EMAIL")
    if not validate_password(password):
        raise AuthServiceError("Password must be at least 8 characters", "WEAK_PASSWORD")

    email = normalize_email(email)
    password_hash = generate_password_hash(password)

    user_doc = create_user_document(name, email, password_hash)
    users_col = mongo.get_collection('users')

    try:
        result = users_col.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id
        return serialize_user(user_doc)
    except DuplicateKeyError:
        raise AuthServiceError("Email is already registered", "EMAIL_ALREADY_EXISTS")

def login_user(data):
    """Business logic for user login."""
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        raise AuthServiceError("Email and password are required", "MISSING_CREDENTIALS")

    email = normalize_email(email)
    users_col = mongo.get_collection('users')
    
    # Generic invalid login response logic
    invalid_creds_error = AuthServiceError("Invalid credentials", "INVALID_CREDENTIALS")
    
    user_doc = users_col.find_one({"email": email})
    if not user_doc:
        raise invalid_creds_error
        
    if not check_password_hash(user_doc['password_hash'], password):
        raise invalid_creds_error
        
    if not user_doc.get('is_active', True):
        raise AuthServiceError("Account is inactive", "ACCOUNT_INACTIVE")

    # Update last login
    now = datetime.datetime.now(datetime.timezone.utc)
    users_col.update_one({"_id": user_doc['_id']}, {"$set": {"last_login": now}})

    # Generate token
    secret = current_app.config.get('JWT_SECRET_KEY')
    expires_in_hours = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 24)
    
    payload = {
        'sub': str(user_doc['_id']),
        'iat': now,
        'exp': now + datetime.timedelta(hours=int(expires_in_hours))
    }
    
    token = jwt.encode(payload, secret, algorithm='HS256')
    
    return {
        "access_token": token,
        "token_type": "Bearer",
        "user": serialize_user(user_doc)
    }
