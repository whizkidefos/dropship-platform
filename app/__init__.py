from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery
from config import Config
from app.tasks import init_celery

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
    
    # Authentication
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Initialize Celery
    init_celery(app)
    
    # Register blueprints
    from app.routes.auth import auth
    from app.routes.products import products
    from routes.admin import admin
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(products)
    app.register_blueprint(admin)
    
    
    # Register routes
    @app.route('/')
    def home():
        return render_template('home.html')
    
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    

    
    return app