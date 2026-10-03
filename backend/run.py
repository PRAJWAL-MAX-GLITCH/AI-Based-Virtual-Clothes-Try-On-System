import os
from app import create_app

# Get configuration name from environment variable, default to 'development'
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    # Run the application
    app.run(host='0.0.0.0', port=port)
