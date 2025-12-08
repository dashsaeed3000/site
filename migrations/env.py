from logging.config import fileConfig
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    BASE_DIR = Path(__file__).resolve().parents[1]
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
fileConfig(config.config_file_name)

# Override sqlalchemy.url from environment variable if set
# This allows using DB_URI from .env or environment instead of hardcoded alembic.ini value
db_uri = os.getenv('DB_URI')
if db_uri:
    config.set_main_option('sqlalchemy.url', db_uri)
    # Debug: print which DB URI is being used (hide password for security)
    import re
    safe_uri = re.sub(r':([^:@]+)@', r':****@', db_uri)
    print(f"[Alembic] Using DB_URI from environment: {safe_uri}")
else:
    ini_url = config.get_main_option("sqlalchemy.url")
    if ini_url:
        import re
        safe_uri = re.sub(r':([^:@]+)@', r':****@', ini_url)
        print(f"[Alembic] Using DB_URI from alembic.ini: {safe_uri}")

# add your model's MetaData object here
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.models.models import Base

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py, can be acquired:
# my_important_option = config.get_main_option("my_important_option")

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        # Fallback: try to get from settings if DB_URI not set
        try:
            from app.config.settings import settings
            url = settings.DB_URI
        except Exception as e:
            raise ValueError(f"No database URL configured. Set DB_URI environment variable or configure alembic.ini. Error: {e}")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Get URL from config (which may have been overridden by DB_URI env var)
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        # Fallback: try to get from settings if DB_URI not set
        try:
            from app.config.settings import settings
            url = settings.DB_URI
        except Exception as e:
            raise ValueError(f"No database URL configured. Set DB_URI environment variable or configure alembic.ini. Error: {e}")
    
    # Create engine directly from URL to ensure we use the correct connection string
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
