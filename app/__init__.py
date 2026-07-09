"""
Flask Application Factory
Initializes and configures the Flask app with extensions and API routes.
"""

import os
from flask import Flask, jsonify, redirect, request, url_for
from flask_cors import CORS
from flask_login import LoginManager
from app.models import User, db
from app.routes import register_routes


def create_app(config_name='development'):
    """
    Application Factory Pattern
    Creates and configures Flask app instance
    """
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///shop.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    is_production = os.environ.get('FLASK_ENV') == 'production' or os.environ.get('ENVIRONMENT') == 'production'
    app.config['SESSION_COOKIE_SAMESITE'] = 'None' if is_production else 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = is_production

    # Initialize extensions
    db.init_app(app)
    allowed_origins = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": [origin.strip() for origin in allowed_origins if origin.strip()]}})

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for session management"""
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('login'))

    register_routes(app)

    # Create database tables automatically on startup
    with app.app_context():
        db.create_all()

    return app
