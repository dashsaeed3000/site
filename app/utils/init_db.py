import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os
from pathlib import Path

# Base project directory (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parents[2]

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except Exception:
    # dotenv is optional; if it's not installed or .env missing, we continue
    pass

# Use DB_URI from environment, or default to localhost for local development
default_host = 'localhost' if os.getenv('DOCKER_ENV') != 'true' else 'db'
DB_URI = os.getenv("DB_URI", f"mysql+pymysql://root:password@{default_host}:3306/maten")

def create_database_if_not_exists():
    # Parse DB_URI to get DB name
    from urllib.parse import urlparse
    url = urlparse(DB_URI)
    db_name = url.path.lstrip('/')  # "mydb"
    
    # Connect to MySQL without specifying DB
    tmp_uri = DB_URI.replace(f"/{db_name}", "/")
    engine = create_engine(tmp_uri)
    
    try:
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
            print(f"Database '{db_name}' exists or created successfully.")
    except OperationalError as e:
        print("Error connecting to MySQL:", e)

def run_migrations():
    """Apply Alembic migrations after DB exists.

    This uses Alembic's Python API and ensures the correct alembic.ini
    from the project root is used. If something fails we catch exceptions
    and print helpful diagnostics so `python -m app.main` won't crash silently.
    """
    try:
        from alembic.config import Config
        from alembic import command

        alembic_cfg_path = BASE_DIR / 'alembic.ini'
        if not alembic_cfg_path.exists():
            print(f"Alembic config not found at {alembic_cfg_path}; skipping migrations.")
            return

        cfg = Config(str(alembic_cfg_path))

        # Ensure DB_URI is provided to Alembic (overrides ini)
        if DB_URI:
            cfg.set_main_option('sqlalchemy.url', DB_URI)

        # Set script location relative to project (helps in some deploys)
        cfg.set_main_option('script_location', str(BASE_DIR / 'migrations'))

        print("Running Alembic migrations...")
        command.upgrade(cfg, 'head')
        print("Migrations applied successfully.")
    except Exception as e:
        print("Failed to run migrations:", e)
        print("If Alembic isn't installed or DB is unreachable, migrations are skipped.")

if __name__ == "__main__":
    create_database_if_not_exists()
    run_migrations()
