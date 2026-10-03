"""
app/utils/errors.py

Centralized exception hierarchy for consistent error handling.
"""

class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, status_code: int = 400, code: str = "BAD_REQUEST"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code

class ValidationError(AppError):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR"):
        super().__init__(message, 400, code)

class AuthError(AppError):
    def __init__(self, message: str, code: str = "UNAUTHORIZED"):
        super().__init__(message, 401, code)

class ForbiddenError(AppError):
    def __init__(self, message: str, code: str = "FORBIDDEN"):
        super().__init__(message, 403, code)

class NotFoundError(AppError):
    def __init__(self, message: str, code: str = "NOT_FOUND"):
        super().__init__(message, 404, code)

class ConflictError(AppError):
    def __init__(self, message: str, code: str = "CONFLICT"):
        super().__init__(message, 409, code)

class PayloadTooLargeError(AppError):
    def __init__(self, message: str, code: str = "PAYLOAD_TOO_LARGE"):
        super().__init__(message, 413, code)

class UnsupportedMediaTypeError(AppError):
    def __init__(self, message: str, code: str = "UNSUPPORTED_MEDIA_TYPE"):
        super().__init__(message, 415, code)

class InternalServerError(AppError):
    def __init__(self, message: str = "An internal server error occurred", code: str = "INTERNAL_SERVER_ERROR"):
        super().__init__(message, 500, code)
