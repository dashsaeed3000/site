import os
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parents[2]
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    # python-dotenv not installed, skip loading .env
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

    def flask_config(self):
        return {
            'SECRET_KEY': self.SECRET_KEY,
            'WTF_CSRF_TIME_LIMIT': self.WTF_CSRF_TIME_LIMIT,
            'ENV': self.FLASK_ENV,
        }

settings = Settings()
