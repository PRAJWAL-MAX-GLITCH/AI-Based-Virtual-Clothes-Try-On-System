from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    """Standard format for successful API responses."""
    if data is None:
        data = {}
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status_code

def error_response(message="An error occurred", status_code=400, error=None):
    """Standard format for error API responses."""
    if error is None:
        error = {}
    return jsonify({
        "success": False,
        "message": message,
        "error": error
    }), status_code
