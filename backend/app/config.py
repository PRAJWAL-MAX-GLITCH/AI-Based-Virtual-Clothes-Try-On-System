import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Resolve the backend root directory (parent of the app/ package)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 24))

    # ── File Upload ──────────────────────────────────────────────────────────
    # Flask's built-in body-size guard (bytes). Default: 5 MB.
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))

    # Absolute path to the upload root.  Resolved relative to backend/ if a
    # relative path is supplied so the server works from any working directory.
    _upload_env = os.getenv('UPLOAD_FOLDER', '')
    UPLOAD_FOLDER = (
        _upload_env if os.path.isabs(_upload_env)
        else os.path.join(_BASE_DIR, 'uploads')
    )

    RESULT_FOLDER = os.path.join(_BASE_DIR, 'results')

    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # ── Image Preprocessing ──────────────────────────────────────────────────
    # Target canvas size for the preprocessing pipeline.
    # Both person and clothing images are normalised to this resolution.
    PREPROCESS_TARGET_WIDTH  = int(os.getenv('PREPROCESS_TARGET_WIDTH',  768))
    PREPROCESS_TARGET_HEIGHT = int(os.getenv('PREPROCESS_TARGET_HEIGHT', 1024))

    # Colour used to fill the padded area (RGB). White is conventional for
    # clothing images; it is also a safe default for person images.
    PREPROCESS_PAD_COLOR = (255, 255, 255)

    # Minimum acceptable input dimensions before the image is rejected.
    PREPROCESS_MIN_WIDTH  = int(os.getenv('PREPROCESS_MIN_WIDTH',  64))
    PREPROCESS_MIN_HEIGHT = int(os.getenv('PREPROCESS_MIN_HEIGHT', 64))

    # ── Pose Detection (MediaPipe) ───────────────────────────────────────────
    # Minimum confidence for a person to be considered detected.
    POSE_MIN_DETECTION_CONFIDENCE = float(os.getenv('POSE_MIN_DETECTION_CONFIDENCE', 0.5))
    # Minimum confidence for landmark tracking.
    POSE_MIN_TRACKING_CONFIDENCE  = float(os.getenv('POSE_MIN_TRACKING_CONFIDENCE',  0.5))
    # Minimum landmark visibility score to consider a landmark "reliable".
    POSE_MIN_VISIBILITY           = float(os.getenv('POSE_MIN_VISIBILITY', 0.5))
    # Absolute path to the MediaPipe PoseLandmarker .task model file.
    POSE_MODEL_PATH = os.getenv(
        'POSE_MODEL_PATH',
        os.path.join(_BASE_DIR, 'models', 'pose_landmarker_full.task')
    )

    # ── Database ─────────────────────────────────────────────────────────────
    MONGO_URI     = os.environ.get('MONGO_URI',     'mongodb://localhost:27017/virtual_try_on')
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'virtual_try_on')

    # ── Server ───────────────────────────────────────────────────────────────
    PORT  = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'

    CORS_ORIGINS = [
        o.strip()
        for o in os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:3001').split(',')
    ]


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
