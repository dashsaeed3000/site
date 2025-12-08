import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import os
from pathlib import Path

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parents[2]
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

# Use DB_URI from environment, or default to localhost for local development
default_host = 'localhost' if os.getenv('DOCKER_ENV') != 'true' else 'db'
DB_URI = os.getenv("DB_URI", f"mysql+pymysql://root:password@{default_host}:3306/shop")

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
    """Apply Alembic migrations after DB exists."""
    import subprocess
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("Migrations applied successfully.")

if __name__ == "__main__":
    create_database_if_not_exists()
    run_migrations()
