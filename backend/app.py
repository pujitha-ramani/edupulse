from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from datetime import timedelta
import os

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # ── Configuration ──────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'edupulse-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(app.instance_path, 'edupulse.db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-edupulse')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    # Mail config (update with real SMTP for production)
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@edupulse.edu')

    # ── Extensions ─────────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    CORS(app, origins=['*'], supports_credentials=True)

    # ── Ensure instance folder exists ──────────────────────────
    os.makedirs(app.instance_path, exist_ok=True)

    # ── Register Blueprints ────────────────────────────────────
    from routes.auth_routes import auth_bp
    from routes.event_routes import event_bp
    from routes.registration_routes import reg_bp
    from routes.user_routes import user_bp
    from routes.analytics_routes import analytics_bp
    from routes.feedback_routes import feedback_bp
    from routes.notification_routes import notif_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(event_bp, url_prefix='/api/events')
    app.register_blueprint(reg_bp, url_prefix='/api/registrations')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
    app.register_blueprint(notif_bp, url_prefix='/api/notifications')

    # ── Serve Frontend ─────────────────────────────────────────
    from flask import send_from_directory
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(frontend_dir, path)):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, 'index.html')

    # ── Init DB + Seed Data ────────────────────────────────────
    with app.app_context():
        db.create_all()
        from seed import seed_database
        seed_database()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
