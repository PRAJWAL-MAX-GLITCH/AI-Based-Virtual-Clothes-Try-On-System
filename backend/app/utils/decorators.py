from functools import wraps
from flask import request, current_app
import jwt
from app.extensions import mongo
from app.utils.response import error_response
from app.models.user import serialize_user
from bson.objectid import ObjectId
from bson.errors import InvalidId

def jwt_required():
    """
    Decorator to protect routes that require a valid JWT.
    Extracts the user from the token and injects it into the route function.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                token = request.args.get('token')
                
            if not token:
                return error_response(
                    message="Missing or invalid Authorization token",
                    status_code=401,
                    error={"code": "MISSING_TOKEN"}
                )
            
            try:
                # Decode the token
                secret = current_app.config.get('JWT_SECRET_KEY')
                payload = jwt.decode(token, secret, algorithms=['HS256'])
                
                # Fetch user from DB
                user_id = payload.get('sub')
                users_col = mongo.get_collection('users')
                
                try:
                    user_doc = users_col.find_one({"_id": ObjectId(user_id)})
                except InvalidId:
                    user_doc = None
                    
                if not user_doc:
                    return error_response(
                        message="User not found",
                        status_code=401,
                        error={"code": "INVALID_TOKEN"}
                    )
                    
                if not user_doc.get('is_active', True):
                    return error_response(
                        message="Account is inactive",
                        status_code=403,
                        error={"code": "ACCOUNT_INACTIVE"}
                    )
                    
                # Inject serialized user into kwargs
                kwargs['current_user'] = serialize_user(user_doc)
                return f(*args, **kwargs)
                
            except jwt.ExpiredSignatureError:
                return error_response(
                    message="Token has expired",
                    status_code=401,
                    error={"code": "EXPIRED_TOKEN"}
                )
            except jwt.InvalidTokenError:
                return error_response(
                    message="Invalid token",
                    status_code=401,
                    error={"code": "INVALID_TOKEN"}
                )
        return decorated_function
    return decorator

def admin_required():
    """
    Decorator to ensure the authenticated user is an admin.
    Must be chained AFTER @jwt_required().
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user or current_user.get('role') != 'admin':
                return error_response(
                    message="Admin privileges required",
                    status_code=403,
                    error={"code": "FORBIDDEN"}
                )
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator
