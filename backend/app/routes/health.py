from flask import Blueprint, current_app
from pymongo.errors import PyMongoError
from app.utils.response import success_response, error_response
from app.extensions import mongo

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return success_response(message="Backend is running")

@health_bp.route('/health/db', methods=['GET'])
def db_health_check():
    """Database health check endpoint to verify MongoDB connectivity."""
    try:
        # Perform a lightweight ping operation
        mongo.ping()
        return success_response(
            message="Database connection successful",
            data={"database": current_app.config.get('MONGO_DB_NAME')}
        )
    except PyMongoError as e:
        # We log the actual error internally
        current_app.logger.error(f"Database health check failed: {str(e)}")
        
        # Return a sanitized error response to the client
        return error_response(
            message="Database connection failed",
            status_code=503,
            error={"code": "DATABASE_UNAVAILABLE"}
        )
