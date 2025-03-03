import os
from pathlib import Path

class Config:
    # Base directory of the application
    BASE_DIR = Path(__file__).resolve().parent
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + str(BASE_DIR / 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload and media settings
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
    GENERATED_CONTENT_DIR = BASE_DIR / 'static' / 'generated_content'
    THUMBNAILS_DIR = BASE_DIR / 'static' / 'thumbnails'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'mp4'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # AI service configurations
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    REPLICATE_API_KEY = os.environ.get('REPLICATE_API_KEY')
    
    # Content generation settings
    DEFAULT_VIDEO_DURATION = 15  # seconds
    DEFAULT_VIDEO_FPS = 30
    DEFAULT_IMAGE_SIZE = (1080, 1080)  # pixels
    DEFAULT_VIDEO_SIZE = (1920, 1080)  # pixels

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    TEMPLATES_AUTO_RELOAD = True
    
    # Development-specific settings
    SQLALCHEMY_ECHO = True  # Log SQL queries
    
class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
    
    # Production-specific settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SSL_REDIRECT = bool(os.environ.get('DYNO'))  # True on Heroku
    
    @classmethod
    def init_app(cls, app):
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Test-specific settings
    UPLOAD_FOLDER = Path('/tmp/test_uploads')
    GENERATED_CONTENT_DIR = Path('/tmp/test_generated')
    THUMBNAILS_DIR = Path('/tmp/test_thumbnails')

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Create required directories if they don't exist
def init_directories(app_config):
    """Initialize required directories for the application"""
    directories = [
        app_config.UPLOAD_FOLDER,
        app_config.GENERATED_CONTENT_DIR,
        app_config.THUMBNAILS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Get current configuration
current_config = config[os.environ.get('FLASK_ENV', 'default')]
init_directories(current_config)