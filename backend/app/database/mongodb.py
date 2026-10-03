import logging
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError, ConnectionFailure

logger = logging.getLogger(__name__)

class MongoDBExtension:
    """
    A lightweight Flask extension to manage the MongoDB connection pool.
    This ensures a single MongoClient instance is reused across requests.
    """
    
    def __init__(self, app=None):
        self.client = None
        self.db = None
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """Initialize the MongoDB client using app configuration."""
        uri = app.config.get('MONGO_URI')
        db_name = app.config.get('MONGO_DB_NAME')
        
        if not uri or not db_name:
            app.logger.warning("MONGO_URI or MONGO_DB_NAME is not set. Database will not be initialized.")
            return

        try:
            # Create a reusable MongoDB client with a short timeout for initial selection
            # to prevent hanging indefinitely if the database is down.
            self.client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            self.db = self.client[db_name]
            app.logger.info(f"MongoDB client initialized for database: {db_name}")
            
            # Register a teardown function to close the client when the application shuts down
            # Note: PyMongo handles its own connection pooling, so we don't close it per-request.
            # However, Flask's teardown_appcontext happens per-request. We don't want to close it there.
            # Instead, we just let the process shutdown handle it or provide a manual close method.
        except Exception as e:
            app.logger.error(f"Failed to initialize MongoDB client: {e}")

    def get_db(self):
        """Retrieve the active database instance."""
        if self.db is None:
            raise RuntimeError("Database not initialized. Call init_app first.")
        return self.db

    def get_collection(self, collection_name: str):
        """
        Retrieve a specific collection from the database.
        Future modules (users, clothing, etc.) will use this to access their collections.
        """
        return self.get_db()[collection_name]

    def ping(self) -> bool:
        """
        Perform a lightweight ping command to verify database connectivity.
        Raises PyMongoError if the connection fails.
        """
        if not self.client:
            raise ConnectionFailure("MongoDB client is not initialized")
            
        try:
            # The 'admin' database is used for server-level commands like ping
            self.client.admin.command('ping')
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB ping failed: {e}")
            raise e
        except PyMongoError as e:
            logger.error(f"MongoDB error during ping: {e}")
            raise e
