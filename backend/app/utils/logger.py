import logging
import sys
from flask import current_app

def setup_logger(app):
    """Set up application logging."""
    log_level = logging.DEBUG if app.config['DEBUG'] else logging.INFO
    
    # Create logger
    logger = logging.getLogger(app.name)
    logger.setLevel(log_level)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    # Avoid attaching to root logger to prevent duplicate logs
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    
    return logger
