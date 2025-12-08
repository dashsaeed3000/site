**Project overview**:
- Lightweight Flask e-commerce sample using provided HTML template files as frontend.
- Layered architecture: presentation (routes), services (business logic), repositories (DB access), models (ORM), config (env settings), payments (pluggable gateways).

**Prerequisites**:
- Docker and docker-compose OR Python 3.11+ and a MySQL instance.

**Quick local dev (docker-compose)**:
1. Copy `.env.example` to `.env` and adjust values.
2. Build and start containers:

```powershell
docker-compose up --build
```

3. Seed DB (inside app container or locally):

```powershell
docker-compose exec app python scripts/seed.py
```

**Migrations**:
- Alembic config is in `alembic.ini` and `migrations/`.
- To run migrations, set `sqlalchemy.url` in `alembic.ini` or use env vars and run:

```powershell
alembic upgrade head
```

**Tests**:
- Run tests with pytest:

```powershell
pytest
```

**Swap DB engine**:
- Change `DB_DIALECT` and `DB_URI` environment variables (e.g., set `DB_URI` to `postgresql+psycopg2://user:pass@host:5432/dbname`).
- The DB adapter is configured in `app/repositories/db.py` and reads `settings.DB_URI`. No other code modifications required.
- Update `requirements.txt` to include the appropriate DB driver (e.g., `psycopg2-binary`).

**Adding a payment gateway**:
- Implement `PaymentGatewayInterface` in `app/payments/`.
- Add concrete gateway, read credentials from environment variables in `app/config/settings.py`.
- Wire gateway into order/payment flow in services and register webhook endpoint in `app/presentation`.

**Environment & secrets**:
- All secrets (DB, STRIPE keys, SECRET_KEY) are read from env vars. See `.env.example`.

**Production**:
- Dockerfile uses Gunicorn; configure number of workers and environment variables accordingly.

**Notes**:
- Passwords hashed with bcrypt via `passlib`.
- CSRF protection provided by `Flask-WTF`.

