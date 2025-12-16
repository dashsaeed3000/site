import os
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parents[2]
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    # python-dotenv not installed — fall back to a minimal .env parser
    BASE_DIR = Path(__file__).resolve().parents[2]
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key:
                        os.environ.setdefault(key, val)
        except Exception:
            # If anything goes wrong reading .env, continue without raising
            pass

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings:
    def __init__(self):
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
        self.DB_DIALECT = os.getenv('DB_DIALECT', 'mysql')
        # Default to localhost for local development, 'db' for Docker
        # Check if we're likely in Docker (environment variable or hostname 'db' exists)
        default_host = 'localhost' if os.getenv('DOCKER_ENV') != 'true' else 'db'
        default_db_uri = f'mysql+pymysql://root:password@{default_host}:3306/shop'
        self.DB_URI = os.getenv('DB_URI', default_db_uri)
        # Templates live in `templates/`.
        self.TEMPLATE_FOLDER = str(BASE_DIR / 'templates')
        # To keep the project lightweight and avoid moving many asset files right now,
        # serve static files from the repository root until we reorganize assets.
        self.STATIC_FOLDER = str(BASE_DIR)
        self.STRIPE_SECRET = os.getenv('STRIPE_SECRET', '')
        self.STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        self.FLASK_ENV = os.getenv('FLASK_ENV', 'production')
        self.WTF_CSRF_TIME_LIMIT = None
        # OAuth settings (configure via environment variables)
        self.GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        self.GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

    def flask_config(self):
        return {
            'SECRET_KEY': self.SECRET_KEY,
            'WTF_CSRF_TIME_LIMIT': self.WTF_CSRF_TIME_LIMIT,
            'ENV': self.FLASK_ENV,
            # Session config for Flask-Session
            'SESSION_TYPE': os.getenv('SESSION_TYPE', 'filesystem'),
            'SESSION_PERMANENT': False,
        }

settings = Settings()
