import os
from app.utils.init_db import create_database_if_not_exists, run_migrations
from app import create_app

# Ensure DB exists and tables are migrated
create_database_if_not_exists()
run_migrations()

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
