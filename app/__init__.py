# Single-line justification: using Flask for its simplicity, Jinja2 templating, and wide ecosystem for small to medium e-commerce apps.
# App factory and blueprint registration
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from .config.settings import settings

csrf = CSRFProtect()

def create_app():
    # Use explicit template and static folders configured via env/settings
    app = Flask(__name__, template_folder=settings.TEMPLATE_FOLDER, static_folder=getattr(settings, 'STATIC_FOLDER', None), static_url_path='/static')
    app.config.from_mapping(settings.flask_config())

    csrf.init_app(app)

    # Add Persian date filter to Jinja2
    from .utils.persian_date import to_persian_date
    app.jinja_env.filters['persian_date'] = to_persian_date

    # Import and register blueprints
    from .presentation.routes import main_bp
    from .presentation.api import api_bp
    from .presentation.admin import admin_bp
    from .presentation.payments import payments_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    # Legacy products admin (kept but moved away from /admin to avoid conflict with Flask-Admin)
    app.register_blueprint(admin_bp, url_prefix='/dashboard/products')

    # Initialize admin area (Flask-Login and Flask-Admin)
    from admin_area import init_admin_area
    init_admin_area(app)

    # Attach extensions (SQLAlchemy engine is created lazily in repositories)

    return app
