help:
	@echo "Commands: migrate, seed, test, run"

migrate:
	alembic upgrade head

seed:
	python scripts/seed.py

test:
	pytest

run:
	python -m app.main
