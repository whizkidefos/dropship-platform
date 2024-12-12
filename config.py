import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or '188880670f5695ff4ee30b0c74b2ff9c6a35c075883f1ca8'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///dropship.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Debug Toolbar
    DEBUG_TB_ENABLED = os.getenv('FLASK_ENV') == 'development'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    # Development specific
    if os.getenv('FLASK_ENV') == 'development':
        EXPLAIN_TEMPLATE_LOADING = True
        TEMPLATES_AUTO_RELOAD = True
        SEND_FILE_MAX_AGE_DEFAULT = 0
    
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') != 'development'
    
    
    # Upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://redis:6379/0'
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Stripe
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')