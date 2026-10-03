"""
app/utils/error_handlers.py

Registers global error handlers with the Flask app.
"""

from flask import current_app
from werkzeug.exceptions import RequestEntityTooLarge, NotFound, MethodNotAllowed, UnsupportedMediaType, Forbidden, HTTPException
from app.utils.errors import AppError
from app.utils.response import error_response

def register_error_handlers(app):
    
    @app.errorhandler(AppError)
    def handle_app_error(e):
        if e.status_code >= 500:
            app.logger.error(f"Internal AppError: {e.message}")
        else:
            app.logger.warning(f"AppError ({e.status_code}): {e.message}")
        return error_response(e.message, e.status_code, {"code": e.code})

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_payload(e):
        app.logger.warning("Request payload too large")
        return error_response("File too large", 413, {"code": "PAYLOAD_TOO_LARGE"})

    @app.errorhandler(UnsupportedMediaType)
    def handle_unsupported_media(e):
        return error_response("Unsupported media type", 415, {"code": "UNSUPPORTED_MEDIA_TYPE"})

    @app.errorhandler(NotFound)
    def handle_not_found(e):
        return error_response("Resource not found", 404, {"code": "NOT_FOUND"})

    @app.errorhandler(MethodNotAllowed)
    def handle_method_not_allowed(e):
        return error_response("Method not allowed", 405, {"code": "METHOD_NOT_ALLOWED"})

    @app.errorhandler(Forbidden)
    def handle_forbidden(e):
        return error_response("Access forbidden", 403, {"code": "FORBIDDEN"})

    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        # Re-raise HTTP exceptions so Flask's own HTTP handlers can process them
        if isinstance(e, HTTPException):
            return error_response(e.description or "HTTP Error", e.code, {"code": str(e.name).upper().replace(' ', '_')})
        # We NEVER leak stack traces to the client
        app.logger.error(f"Unexpected Exception: {str(e)}", exc_info=True)
        return error_response("An internal server error occurred", 500, {"code": "INTERNAL_SERVER_ERROR"})
