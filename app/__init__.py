from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
from config import Config

db = SQLAlchemy()
migrate = Migrate()
celery = Celery(__name__)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure Celery
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # Authentication
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from app.routes.auth import auth
    from app.routes.products import products
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(products)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    # Register routes
    @app.route('/')
    def home():
        return 'Welcome to Dropship Platform!'
    
    return app