# Database operations

Use PostgreSQL as the source of truth. Start the local service with `docker compose up -d postgres`, then run `alembic upgrade head` and `python scripts/seed.py` from `backend`.

Tests use an isolated SQLite database only for self-contained test execution; it does not replace PostgreSQL for development or deployment.
