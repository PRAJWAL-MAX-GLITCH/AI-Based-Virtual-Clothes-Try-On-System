import os
from app import create_app

# Get configuration name from environment variable, default to 'development'
# Support both FLASK_ENV and FLASK keys, handle case-insensitive values
config_name = os.getenv('FLASK_ENV') or os.getenv('FLASK', 'development')
config_name = config_name.lower().strip()  # normalize: 'Production' -> 'production'
app = create_app(config_name)

if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    # Run the application
    app.run(host='0.0.0.0', port=port)
