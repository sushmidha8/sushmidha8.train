import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

class Config:
    # App Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SERVER_NAME = os.environ.get('SERVER_NAME', 'localhost:5000')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Cache Configuration
    CACHE_TYPE = 'RedisCache' if os.environ.get('REDIS_URL') else 'SimpleCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Admin Configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@railway.com')
    
    # Performance Settings
    JSONIFY_PRETTYPRINT_REGULAR = False
    SQLALCHEMY_RECORD_QUERIES = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 30,
        'max_overflow': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    PROPAGATE_EXCEPTIONS = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}