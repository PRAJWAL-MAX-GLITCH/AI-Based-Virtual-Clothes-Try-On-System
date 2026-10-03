"""
Flask extensions are initialized here to avoid circular dependencies.
"""
from flask_cors import CORS
from .database.mongodb import MongoDBExtension

# Initialize extensions
cors = CORS()
mongo = MongoDBExtension()
