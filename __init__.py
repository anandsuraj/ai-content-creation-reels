import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///content_platform.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    
    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Import and register blueprints
    from ai_content_platform.routes.auth import auth as auth_blueprint
    from ai_content_platform.routes.content import content as content_blueprint
    from ai_content_platform.routes.api import api as api_blueprint
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(content_blueprint)
    app.register_blueprint(api_blueprint)
    
    # Import models for create_all
    from ai_content_platform.models.user import User
    from ai_content_platform.models.content import Content
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
