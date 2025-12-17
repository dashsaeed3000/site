This repository is a Flask-based website (directory `app/`) using SQLAlchemy for models and a small admin area in `admin_area/`.

Purpose
- Help AI coding agents make safe, focused changes: add features, fix bugs, and follow existing conventions.

Big-picture architecture (what to know first)
- Web app: `app/` is the runtime Flask application. Main routes are in `app/presentation/routes.py` (single blueprint `main_bp`).
- Models: application models live under `app/models/` and the admin/user model is under `admin_area/models.py` (SQLAlchemy `Base` classes).
- DB/session: the project uses a session factory `app/repositories/db.py` exposing `get_session()` — use `with next(get_session()) as db:` to get a transactional SQLAlchemy session.
- Services: business logic is separated into `app/services/*` (e.g. `user_service.py`, `product_service.py`) — prefer adding logic there rather than in routes.
- Presentation: Jinja templates are under `templates/` and `admin_area/templates/` — follow RTL layout and existing CSS classes.

Key files to inspect when making changes
- `app/presentation/routes.py`: all public routes, OAuth callbacks, session usage.
- `admin_area/models.py`: `User` model and helper getters (`get_user_by_username`, `get_user_by_id`). If you change the user schema, update these helpers and create migrations.
- `app/services/user_service.py`: central place to create/find users and normalize phone numbers.
- `app/repositories/db.py`: session factory — use it rather than creating engine/sessions directly.
- `app/config/settings.py`: environment-driven config like `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI`.

Conventions and patterns
- Database sessions: call `with next(get_session()) as db:` in routes or services to get a session and ensure commit/rollback.
- User creation: use `UserService.create_user_from_phone(...)` for both SMS and OAuth-created users — it will normalize phone and ensure username uniqueness.
- Passwords: User model uses `set_password`/`check_password` helpers (bcrypt) — do not set `password_hash` directly.
- Templates: project is RTL and Persian strings are embedded; maintain existing class names and structure for consistent styling.
- OAuth: the code uses `current_app.oauth.google.authorize_redirect(...)` and `authorize_access_token()` flow — inspect `app/__init__.py` or where `oauth` is configured in app factory if you need to change this.

Testing, running, and migrations
- Run app (development): project doesn't include a single runner script in repo root; start the Flask app according to project README or the app factory. If you use a virtualenv:

```powershell
# from workspace root (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# set FLASK_APP in PowerShell:
$env:FLASK_APP='app.main'
flask run --host=0.0.0.0
```

- Migrations: this repo uses Alembic files under `migrations/`. When you change models, create an Alembic revision and upgrade. Example:

```powershell
alembic revision --autogenerate -m "add mobile to users"
alembic upgrade head
```

Safe editing rules for AI agents (high-value, non-generic)
- Never change `admin_area/models.py` primary key names or remove columns without adding a migration. If adding columns, also add an Alembic revision.
- When modifying a route that uses `session` or `flask-login`, preserve the existing session keys (e.g., `session['oauth_user']`, `redirect_after_login`) unless you update all call sites.
- For DB writes, prefer using `UserService` and other services. If adding direct DB access in routes, use `with next(get_session()) as db:` and call `db.flush()`/`db.commit()` appropriately.
- When creating usernames automatically, follow existing uniqueness strategy (append numeric suffix). `UserService.create_user_from_phone` contains a suitable pattern; reuse it.
- For OAuth callbacks: validate `state` if present, exchange token via configured `oauth` object, then call service-layer upsert; do not store raw OAuth tokens in session.

Integration points and external dependencies
- Google OAuth: configured via `current_app.oauth.google` — ensure `GOOGLE_REDIRECT_URI` matches console settings and callbacks use `_external=True, _scheme='https'` where the site is HTTPS.
- SMS/phone verification: exists in `app/services/phone_verification_service.py` — if you change activation flows, update that service and templates that render forms.
- Payments: `app/payments/*` contains gateway implementations — don't change payment interface signatures.

Examples from repo
- Getting a DB session in routes:

```py
with next(get_session()) as db:
    user_service = UserService(db)
    user = user_service.get_user_by_email(email)
```

- OAuth login starter in `routes.py`:

```py
redirect_uri = url_for('main.auth_google_callback', _external=True, _scheme='https')
return current_app.oauth.google.authorize_redirect(redirect_uri)
```

When to ask the maintainer (rather than guessing)
- If a schema change affects existing users (e.g., making a column non-nullable), ask for migration policy and backup plan.
- If you need to change configuration names or add environment variables, confirm deployment environment (how secrets are injected).

If any part of this file is unclear or you want sample templates (badge prompting for mobile after OAuth), reply and I'll expand with concrete code snippets and a migration example.

---
Last updated: automatic AI scan of repository structure. Please review and request edits for any missing local workflows.
