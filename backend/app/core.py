from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any
from uuid import UUID, uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import Session

ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")
    database_url: str = "postgresql+psycopg://pathforge:pathforge@localhost:5432/pathforge"
    jwt_secret: str = "development-only-change-me-before-deploying-please"
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    frontend_origin: str = "http://localhost:3000"
    frontend_origins: str = ""
    environment: str = "development"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash-lite"
    ai_timeout_seconds: int = 30

    @property
    def allowed_frontend_origins(self) -> list[str]:
        origins = {
            origin.strip().rstrip("/")
            for origin in (self.frontend_origin, *self.frontend_origins.split(","))
            if origin.strip()
        }
        if self.environment.lower() == "production":
            # Keep both the original and current production Vercel aliases
            # available while the old domain is retired.
            origins.update({
                "https://pathforge-ai.vercel.app",
                "https://pathforge-ai-one.vercel.app",
            })
        # Local dev servers may be opened through either loopback hostname.
        if self.environment.lower() != "production":
            loopback_pairs = {
                "http://localhost:3000": "http://127.0.0.1:3000",
                "http://127.0.0.1:3000": "http://localhost:3000",
            }
            alias = loopback_pairs.get(self.frontend_origin.rstrip("/"))
            if alias:
                origins.add(alias)
        return sorted(origins)

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.environment.lower() == "production":
            if self.jwt_secret.startswith("development-only-") or len(self.jwt_secret) < 32:
                raise ValueError("Production requires a unique JWT_SECRET with at least 32 characters")
            if not self.frontend_origin.startswith("https://"):
                raise ValueError("Production FRONTEND_ORIGIN must use HTTPS")
            if not self.database_url.lower().startswith("postgresql"):
                raise ValueError("Production requires PostgreSQL")
        return self


settings = Settings()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)


def utcnow() -> datetime:
    return datetime.now(UTC)


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def token_hash(token: str) -> str:
    return sha256(token.encode()).hexdigest()


def create_token(subject: UUID, kind: str, expires: timedelta) -> tuple[str, str]:
    jti = str(uuid4())
    now = utcnow()
    payload = {"sub": str(subject), "typ": kind, "jti": jti, "iat": now, "exp": now + expires}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256"), jti


def decode_token(token: str, expected_kind: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc
    if payload.get("typ") != expected_kind:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return payload


def api_error(code: str, message: str, http_status: int, details: dict | None = None) -> HTTPException:
    return HTTPException(http_status, {"code": code, "message": message, "details": details or {}})


def get_db():
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)], db: DbSession
):
    from app.models import User

    if not credentials:
        raise api_error("UNAUTHENTICATED", "Authentication is required", 401)
    payload = decode_token(credentials.credentials, "access")
    user = db.get(User, UUID(payload["sub"]))
    if not user or not user.is_active:
        raise api_error("UNAUTHENTICATED", "Account is unavailable", 401)
    return user


CurrentUser = Annotated[Any, Depends(get_current_user)]


def require_admin(user: CurrentUser):
    if user.role != "ADMIN":
        raise api_error("FORBIDDEN", "Administrator access is required", 403)
    return user


AdminUser = Annotated[Any, Depends(require_admin)]


def enforce_same_origin(request: Request) -> None:
    """CSRF guard for cookie-bearing refresh/logout calls."""
    origin = request.headers.get("origin")
    if origin and origin.rstrip("/") not in settings.allowed_frontend_origins:
        raise api_error("CSRF_REJECTED", "Cross-origin request rejected", 403)

