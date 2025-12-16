# Single-line justification: using Flask for its simplicity, Jinja2 templating, and wide ecosystem for small to medium e-commerce apps.
# App factory and blueprint registration
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from .config.settings import settings
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from flask import current_app

csrf = CSRFProtect()

def create_app():
    # Use explicit template and static folders configured via env/settings
    app = Flask(__name__, template_folder=settings.TEMPLATE_FOLDER, static_folder=getattr(settings, 'STATIC_FOLDER', None), static_url_path='/static')
    app.config.from_mapping(settings.flask_config())

    csrf.init_app(app)

    # Configure server-side sessions for OAuth usage
    app.config.setdefault('SESSION_TYPE', 'filesystem')
    app.config.setdefault('SESSION_PERMANENT', False)
    Session(app)

    # Initialize OAuth (Authlib)
    oauth = OAuth(app)
    # Register Google OAuth provider using OpenID Connect discovery
    google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None) or None
    google_client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', None) or None
    if google_client_id and google_client_secret:
        oauth.register(
            name='google',
            client_id=google_client_id,
            client_secret=google_client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )
    # Expose oauth on app for blueprints to use
    app.oauth = oauth

    # Add Persian date filter to Jinja2
    from .utils.persian_date import to_persian_date
    app.jinja_env.filters['persian_date'] = to_persian_date

    # Import and register blueprints
    from .presentation.routes import main_bp
    from .presentation.api import api_bp
    from .presentation.payments import payments_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    # NOTE: legacy admin blueprint `presentation.admin` was removed from registration
    # to rely solely on the Sash-based Flask-Admin UI under `/admin/`.

    # Initialize admin area (Flask-Login and Flask-Admin)
    from admin_area import init_admin_area
    init_admin_area(app)

    # Attach extensions (SQLAlchemy engine is created lazily in repositories)

    return app
