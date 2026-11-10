from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core import settings


def normalize_database_url(database_url: str) -> str:
    """Normalize provider URLs for psycopg while retaining TLS requirements.

    Some PostgreSQL-compatible providers add ``channel_binding=require`` to
    their connection strings. Older libpq builds reject that value, so prefer
    channel binding when supported and keep ``sslmode=require`` intact.
    """
    # Dashboard secrets are sometimes pasted with shell/.env quote marks.
    url = make_url(database_url.strip().strip("\"'"))
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+psycopg")

    if url.drivername == "postgresql+psycopg":
        query = dict(url.query)
        if "channel_binding" in query:
            # Psycopg/libpq versions in the deployment image can reject
            # `require` (including a quoted value copied from a .env line).
            # `prefer` keeps channel binding when supported and falls back
            # otherwise; TLS remains enforced by sslmode=require.
            query["channel_binding"] = "prefer"
            url = url.set(query=query)
        return url.render_as_string(hide_password=False)

    return database_url


engine = create_engine(normalize_database_url(settings.database_url), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass

