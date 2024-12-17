# app/__init__.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
import flask_monitoringdashboard as dashboard
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
toolbar = DebugToolbarExtension()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Development tools
    if app.debug:
        toolbar.init_app(app)
        dashboard.bind(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    from app.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
     
    # Register main routes
    @app.route('/')
    def home():
        return render_template('home.html')
    
    # Register product routes
    from app.models.product import Product
    @app.route('/products')
    def products():
        return render_template('products.html', products=Product.query.all())
    
    
    # Register blueprints
    from app.routes.auth import auth
    from app.routes.admin import admin
    from app.routes.products import products
    from app.routes.cart import cart
    from app.routes.checkout import checkout
    from app.routes.wishlist import wishlist
    
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix=str('/admin'))
    app.register_blueprint(products, url_prefix='/products')
    app.register_blueprint(cart, url_prefix='/cart')
    app.register_blueprint(checkout, url_prefix='/checkout')
    app.register_blueprint(wishlist, url_prefix='/wishlist')
    
    # Ensure the upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html', error=str(error)), 500
    
    if app.debug:
        @app.after_request
        def add_development_headers(response):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        
    return app